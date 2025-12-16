"""Two-pass M6803 assembler.

Pass 1: Build symbol table and calculate instruction addresses
Pass 2: Generate machine code with resolved label references
"""

from __future__ import annotations

from supertape.core.asm.directives import DirectiveProcessor
from supertape.core.asm.errors import (
    BranchOutOfRangeError,
    InvalidAddressingModeError,
    UnknownInstructionError,
)
from supertape.core.asm.lexer import Lexer
from supertape.core.asm.opcodes import get_opcode, get_valid_modes, is_branch_instruction
from supertape.core.asm.parser import Directive, Instruction, Parser
from supertape.core.asm.symbols import SymbolTable
from supertape.core.disasm.m6803 import AddressingMode


class M6803Assembler:
    """
    Two-pass assembler for Motorola 6803 assembly language.

    Pass 1: Build symbol table, calculate addresses
    Pass 2: Generate machine code
    """

    def __init__(self) -> None:
        """Initialize assembler."""
        self.symbols = SymbolTable()
        self.directives = DirectiveProcessor()

    def _calculate_instruction_length(self, instruction: Instruction, line: int) -> int:
        """
        Calculate the length of an instruction in bytes.

        Args:
            instruction: Instruction to measure
            line: Line number for error reporting

        Returns:
            Instruction length in bytes
        """
        mnemonic = instruction.mnemonic

        # Determine addressing mode
        if instruction.operand is None:
            # No operand - must be inherent mode
            mode = AddressingMode.INHERENT
        else:
            mode = instruction.operand.mode

            # For branch instructions, always use RELATIVE mode
            if is_branch_instruction(mnemonic):
                mode = AddressingMode.RELATIVE

        # Get opcode and length
        try:
            _, length = get_opcode(mnemonic, mode, line)
            return length
        except (UnknownInstructionError, InvalidAddressingModeError):
            # If the exact mode doesn't exist, try to infer
            # For example, DIRECT vs EXTENDED based on value
            if mode == AddressingMode.DIRECT and instruction.operand:
                # Try EXTENDED if DIRECT doesn't work
                try:
                    _, length = get_opcode(mnemonic, AddressingMode.EXTENDED, line)
                    return length
                except (UnknownInstructionError, InvalidAddressingModeError):
                    pass
            raise

    def pass1(self, program: list[Instruction | Directive]) -> None:
        """
        Pass 1: Build symbol table and calculate addresses.

        Args:
            program: List of parsed instructions and directives
        """
        self.symbols.clear()
        self.directives.reset()

        current_address = self.directives.get_origin()

        for statement in program:
            line = statement.line_number

            # Process label if present
            if statement.label:
                self.symbols.define(statement.label, current_address, line)

            # Process directive or instruction
            if isinstance(statement, Directive):
                if statement.directive == "ORG":
                    self.directives.process_org(statement.value, line)
                    current_address = self.directives.get_origin()
                elif statement.directive == "EXC":
                    self.directives.process_exc(statement.value, line)
                elif statement.directive == "DFD":
                    # DFD takes 2 bytes
                    current_address += 2
                elif statement.directive == "DB":
                    # DB takes 1 byte
                    current_address += 1
                elif statement.directive == "LABEL":
                    # Label-only line, no bytes
                    pass
                # FCC/as68 directives
                elif statement.directive == ".SETCPU":
                    self.directives.process_setcpu(statement.value, line)
                elif statement.directive == ".CODE":
                    self.directives.process_code(statement.value, line)
                elif statement.directive == ".DATA":
                    self.directives.process_data(statement.value, line)
                elif statement.directive == ".WORD":
                    # .word takes 2 bytes (alias for DFD)
                    current_address += 2
                elif statement.directive == ".BYTE":
                    # .byte takes 1 byte (alias for DB)
                    current_address += 1
                elif statement.directive == ".EXPORT":
                    self.directives.process_export(statement.value, line)

            elif isinstance(statement, Instruction):
                # Calculate instruction length and advance address
                length = self._calculate_instruction_length(statement, line)
                current_address += length

    def _encode_instruction(self, instruction: Instruction, current_address: int) -> list[int]:
        """
        Encode an instruction to machine code bytes.

        Args:
            instruction: Instruction to encode
            current_address: Current program counter address

        Returns:
            List of bytes for this instruction
        """
        line = instruction.line_number
        mnemonic = instruction.mnemonic
        bytes_out: list[int] = []

        # Determine addressing mode and operand value
        if instruction.operand is None:
            # Inherent mode
            mode = AddressingMode.INHERENT
            opcode, _ = get_opcode(mnemonic, mode, line)
            bytes_out.append(opcode)

        else:
            mode = instruction.operand.mode
            value = instruction.operand.value

            # Resolve label references to addresses
            if isinstance(value, str):
                # Label reference
                value = self.symbols.lookup(value, line)

            # For branch instructions, calculate relative offset
            if is_branch_instruction(mnemonic):
                mode = AddressingMode.RELATIVE
                opcode, length = get_opcode(mnemonic, mode, line)

                # Calculate relative offset
                # Offset is from address AFTER the instruction
                target_address = value
                offset = target_address - (current_address + length)

                # Check range (-128 to 127)
                if offset < -128 or offset > 127:
                    raise BranchOutOfRangeError(mnemonic, offset, target_address, current_address, line)

                # Convert to unsigned byte (two's complement)
                if offset < 0:
                    offset_byte = (offset + 256) & 0xFF
                else:
                    offset_byte = offset & 0xFF

                bytes_out.append(opcode)
                bytes_out.append(offset_byte)

            else:
                # Non-branch instruction
                # Try to get opcode with current mode
                try:
                    opcode, length = get_opcode(mnemonic, mode, line)
                except InvalidAddressingModeError:
                    # If mode doesn't work, try to resolve DIRECT vs EXTENDED
                    if mode in (AddressingMode.DIRECT, AddressingMode.EXTENDED):
                        # Try the other mode
                        if value <= 0xFF:
                            # Try DIRECT first
                            valid_modes = get_valid_modes(mnemonic)
                            if AddressingMode.DIRECT in valid_modes:
                                mode = AddressingMode.DIRECT
                                opcode, length = get_opcode(mnemonic, mode, line)
                            else:
                                mode = AddressingMode.EXTENDED
                                opcode, length = get_opcode(mnemonic, mode, line)
                        else:
                            # Must use EXTENDED
                            mode = AddressingMode.EXTENDED
                            opcode, length = get_opcode(mnemonic, mode, line)
                    else:
                        raise

                bytes_out.append(opcode)

                # Add operand bytes based on mode
                if mode == AddressingMode.IMMEDIATE:
                    if length == 2:
                        # 8-bit immediate
                        bytes_out.append(value & 0xFF)
                    elif length == 3:
                        # 16-bit immediate (big-endian)
                        bytes_out.append((value >> 8) & 0xFF)  # MSB
                        bytes_out.append(value & 0xFF)  # LSB

                elif mode == AddressingMode.DIRECT:
                    # Direct page address (8-bit)
                    bytes_out.append(value & 0xFF)

                elif mode == AddressingMode.EXTENDED:
                    # Extended address (16-bit, big-endian)
                    bytes_out.append((value >> 8) & 0xFF)  # MSB
                    bytes_out.append(value & 0xFF)  # LSB

                elif mode == AddressingMode.INDEXED:
                    # Indexed offset (8-bit)
                    bytes_out.append(value & 0xFF)

        return bytes_out

    def pass2(self, program: list[Instruction | Directive]) -> list[int]:
        """
        Pass 2: Generate machine code.

        Args:
            program: List of parsed instructions and directives

        Returns:
            List of machine code bytes
        """
        machine_code: list[int] = []
        current_address = self.directives.get_origin()

        for statement in program:
            line = statement.line_number

            if isinstance(statement, Directive):
                if statement.directive == "ORG":
                    # ORG changes address but generates no code
                    current_address = self.directives.get_origin()
                elif statement.directive == "EXC":
                    # EXC generates no code
                    pass
                elif statement.directive == "DFD":
                    # Define 16-bit word (big-endian)
                    bytes_data = self.directives.process_dfd(statement.value, line)
                    machine_code.extend(bytes_data)
                    current_address += len(bytes_data)
                elif statement.directive == "DB":
                    # Define byte
                    bytes_data = self.directives.process_db(statement.value, line)
                    machine_code.extend(bytes_data)
                    current_address += len(bytes_data)
                elif statement.directive == "LABEL":
                    # Label-only, no code
                    pass
                # FCC/as68 directives
                elif statement.directive == ".SETCPU":
                    # Informational only
                    pass
                elif statement.directive == ".CODE":
                    # Section directive, no code
                    pass
                elif statement.directive == ".DATA":
                    # Section directive, no code
                    pass
                elif statement.directive == ".WORD":
                    # Define 16-bit word (alias for DFD)
                    bytes_data = self.directives.process_word(statement.value, line)
                    machine_code.extend(bytes_data)
                    current_address += len(bytes_data)
                elif statement.directive == ".BYTE":
                    # Define byte (alias for DB)
                    bytes_data = self.directives.process_byte(statement.value, line)
                    machine_code.extend(bytes_data)
                    current_address += len(bytes_data)
                elif statement.directive == ".EXPORT":
                    # Informational only
                    pass

            elif isinstance(statement, Instruction):
                # Encode instruction
                instruction_bytes = self._encode_instruction(statement, current_address)
                machine_code.extend(instruction_bytes)
                current_address += len(instruction_bytes)

        return machine_code

    def assemble(self, source: str) -> tuple[list[int], int, int]:
        """
        Assemble source code to machine code.

        Args:
            source: Assembly source code

        Returns:
            Tuple of (machine_code_bytes, load_address, exec_address)
        """
        # Tokenize
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        # Parse
        parser = Parser(tokens)
        program = parser.parse()

        # Pass 1: Build symbol table
        self.pass1(program.statements)

        # Pass 2: Generate machine code
        machine_code = self.pass2(program.statements)

        # Get load and exec addresses
        load_address = self.directives.get_origin()
        exec_address = self.directives.get_exec(self.symbols)

        return (machine_code, load_address, exec_address)
