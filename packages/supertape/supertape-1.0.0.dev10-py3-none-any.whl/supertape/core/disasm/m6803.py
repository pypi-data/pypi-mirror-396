"""Motorola 6803 disassembler for MC-10 and Alice computers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AddressingMode(Enum):
    """6803 addressing modes."""

    INHERENT = "inh"  # No operands (e.g., NOP, RTS)
    IMMEDIATE = "imm"  # Immediate value (e.g., LDA #$FF)
    DIRECT = "dir"  # Direct page addressing (e.g., LDA $80)
    EXTENDED = "ext"  # Extended addressing (e.g., LDA $4000)
    INDEXED = "idx"  # Indexed addressing (e.g., LDA $00,X)
    RELATIVE = "rel"  # Relative branch (e.g., BRA $+5)


@dataclass
class Instruction:
    """Represents a disassembled instruction."""

    address: int
    opcode: int
    length: int
    mnemonic: str
    mode: AddressingMode
    operand_bytes: list[int]


# Complete 6803 opcode table
# Format: opcode -> (mnemonic, addressing_mode, length)
OPCODE_TABLE: dict[int, tuple[str, AddressingMode, int]] = {
    # Arithmetic operations
    0x80: ("SUBA", AddressingMode.IMMEDIATE, 2),
    0x81: ("CMPA", AddressingMode.IMMEDIATE, 2),
    0x82: ("SBCA", AddressingMode.IMMEDIATE, 2),
    0x83: ("SUBD", AddressingMode.IMMEDIATE, 3),
    0x84: ("ANDA", AddressingMode.IMMEDIATE, 2),
    0x85: ("BITA", AddressingMode.IMMEDIATE, 2),
    0x86: ("LDAA", AddressingMode.IMMEDIATE, 2),
    0x88: ("EORA", AddressingMode.IMMEDIATE, 2),
    0x89: ("ADCA", AddressingMode.IMMEDIATE, 2),
    0x8A: ("ORAA", AddressingMode.IMMEDIATE, 2),
    0x8B: ("ADDA", AddressingMode.IMMEDIATE, 2),
    0x8C: ("CPX", AddressingMode.IMMEDIATE, 3),
    0x8D: ("BSR", AddressingMode.RELATIVE, 2),
    0x8E: ("LDS", AddressingMode.IMMEDIATE, 3),
    0x90: ("SUBA", AddressingMode.DIRECT, 2),
    0x91: ("CMPA", AddressingMode.DIRECT, 2),
    0x92: ("SBCA", AddressingMode.DIRECT, 2),
    0x93: ("SUBD", AddressingMode.DIRECT, 2),
    0x94: ("ANDA", AddressingMode.DIRECT, 2),
    0x95: ("BITA", AddressingMode.DIRECT, 2),
    0x96: ("LDAA", AddressingMode.DIRECT, 2),
    0x97: ("STAA", AddressingMode.DIRECT, 2),
    0x98: ("EORA", AddressingMode.DIRECT, 2),
    0x99: ("ADCA", AddressingMode.DIRECT, 2),
    0x9A: ("ORAA", AddressingMode.DIRECT, 2),
    0x9B: ("ADDA", AddressingMode.DIRECT, 2),
    0x9C: ("CPX", AddressingMode.DIRECT, 2),
    0x9D: ("JSR", AddressingMode.DIRECT, 2),
    0x9E: ("LDS", AddressingMode.DIRECT, 2),
    0x9F: ("STS", AddressingMode.DIRECT, 2),
    0xA0: ("SUBA", AddressingMode.INDEXED, 2),
    0xA1: ("CMPA", AddressingMode.INDEXED, 2),
    0xA2: ("SBCA", AddressingMode.INDEXED, 2),
    0xA3: ("SUBD", AddressingMode.INDEXED, 2),
    0xA4: ("ANDA", AddressingMode.INDEXED, 2),
    0xA5: ("BITA", AddressingMode.INDEXED, 2),
    0xA6: ("LDAA", AddressingMode.INDEXED, 2),
    0xA7: ("STAA", AddressingMode.INDEXED, 2),
    0xA8: ("EORA", AddressingMode.INDEXED, 2),
    0xA9: ("ADCA", AddressingMode.INDEXED, 2),
    0xAA: ("ORAA", AddressingMode.INDEXED, 2),
    0xAB: ("ADDA", AddressingMode.INDEXED, 2),
    0xAC: ("CPX", AddressingMode.INDEXED, 2),
    0xAD: ("JSR", AddressingMode.INDEXED, 2),
    0xAE: ("LDS", AddressingMode.INDEXED, 2),
    0xAF: ("STS", AddressingMode.INDEXED, 2),
    0xB0: ("SUBA", AddressingMode.EXTENDED, 3),
    0xB1: ("CMPA", AddressingMode.EXTENDED, 3),
    0xB2: ("SBCA", AddressingMode.EXTENDED, 3),
    0xB3: ("SUBD", AddressingMode.EXTENDED, 3),
    0xB4: ("ANDA", AddressingMode.EXTENDED, 3),
    0xB5: ("BITA", AddressingMode.EXTENDED, 3),
    0xB6: ("LDAA", AddressingMode.EXTENDED, 3),
    0xB7: ("STAA", AddressingMode.EXTENDED, 3),
    0xB8: ("EORA", AddressingMode.EXTENDED, 3),
    0xB9: ("ADCA", AddressingMode.EXTENDED, 3),
    0xBA: ("ORAA", AddressingMode.EXTENDED, 3),
    0xBB: ("ADDA", AddressingMode.EXTENDED, 3),
    0xBC: ("CPX", AddressingMode.EXTENDED, 3),
    0xBD: ("JSR", AddressingMode.EXTENDED, 3),
    0xBE: ("LDS", AddressingMode.EXTENDED, 3),
    0xBF: ("STS", AddressingMode.EXTENDED, 3),
    0xC0: ("SUBB", AddressingMode.IMMEDIATE, 2),
    0xC1: ("CMPB", AddressingMode.IMMEDIATE, 2),
    0xC2: ("SBCB", AddressingMode.IMMEDIATE, 2),
    0xC3: ("ADDD", AddressingMode.IMMEDIATE, 3),
    0xC4: ("ANDB", AddressingMode.IMMEDIATE, 2),
    0xC5: ("BITB", AddressingMode.IMMEDIATE, 2),
    0xC6: ("LDAB", AddressingMode.IMMEDIATE, 2),
    0xC8: ("EORB", AddressingMode.IMMEDIATE, 2),
    0xC9: ("ADCB", AddressingMode.IMMEDIATE, 2),
    0xCA: ("ORAB", AddressingMode.IMMEDIATE, 2),
    0xCB: ("ADDB", AddressingMode.IMMEDIATE, 2),
    0xCC: ("LDD", AddressingMode.IMMEDIATE, 3),
    0xCE: ("LDX", AddressingMode.IMMEDIATE, 3),
    0xD0: ("SUBB", AddressingMode.DIRECT, 2),
    0xD1: ("CMPB", AddressingMode.DIRECT, 2),
    0xD2: ("SBCB", AddressingMode.DIRECT, 2),
    0xD3: ("ADDD", AddressingMode.DIRECT, 2),
    0xD4: ("ANDB", AddressingMode.DIRECT, 2),
    0xD5: ("BITB", AddressingMode.DIRECT, 2),
    0xD6: ("LDAB", AddressingMode.DIRECT, 2),
    0xD7: ("STAB", AddressingMode.DIRECT, 2),
    0xD8: ("EORB", AddressingMode.DIRECT, 2),
    0xD9: ("ADCB", AddressingMode.DIRECT, 2),
    0xDA: ("ORAB", AddressingMode.DIRECT, 2),
    0xDB: ("ADDB", AddressingMode.DIRECT, 2),
    0xDC: ("LDD", AddressingMode.DIRECT, 2),
    0xDD: ("STD", AddressingMode.DIRECT, 2),
    0xDE: ("LDX", AddressingMode.DIRECT, 2),
    0xDF: ("STX", AddressingMode.DIRECT, 2),
    0xE0: ("SUBB", AddressingMode.INDEXED, 2),
    0xE1: ("CMPB", AddressingMode.INDEXED, 2),
    0xE2: ("SBCB", AddressingMode.INDEXED, 2),
    0xE3: ("ADDD", AddressingMode.INDEXED, 2),
    0xE4: ("ANDB", AddressingMode.INDEXED, 2),
    0xE5: ("BITB", AddressingMode.INDEXED, 2),
    0xE6: ("LDAB", AddressingMode.INDEXED, 2),
    0xE7: ("STAB", AddressingMode.INDEXED, 2),
    0xE8: ("EORB", AddressingMode.INDEXED, 2),
    0xE9: ("ADCB", AddressingMode.INDEXED, 2),
    0xEA: ("ORAB", AddressingMode.INDEXED, 2),
    0xEB: ("ADDB", AddressingMode.INDEXED, 2),
    0xEC: ("LDD", AddressingMode.INDEXED, 2),
    0xED: ("STD", AddressingMode.INDEXED, 2),
    0xEE: ("LDX", AddressingMode.INDEXED, 2),
    0xEF: ("STX", AddressingMode.INDEXED, 2),
    0xF0: ("SUBB", AddressingMode.EXTENDED, 3),
    0xF1: ("CMPB", AddressingMode.EXTENDED, 3),
    0xF2: ("SBCB", AddressingMode.EXTENDED, 3),
    0xF3: ("ADDD", AddressingMode.EXTENDED, 3),
    0xF4: ("ANDB", AddressingMode.EXTENDED, 3),
    0xF5: ("BITB", AddressingMode.EXTENDED, 3),
    0xF6: ("LDAB", AddressingMode.EXTENDED, 3),
    0xF7: ("STAB", AddressingMode.EXTENDED, 3),
    0xF8: ("EORB", AddressingMode.EXTENDED, 3),
    0xF9: ("ADCB", AddressingMode.EXTENDED, 3),
    0xFA: ("ORAB", AddressingMode.EXTENDED, 3),
    0xFB: ("ADDB", AddressingMode.EXTENDED, 3),
    0xFC: ("LDD", AddressingMode.EXTENDED, 3),
    0xFD: ("STD", AddressingMode.EXTENDED, 3),
    0xFE: ("LDX", AddressingMode.EXTENDED, 3),
    0xFF: ("STX", AddressingMode.EXTENDED, 3),
    # Branches
    0x20: ("BRA", AddressingMode.RELATIVE, 2),
    0x22: ("BHI", AddressingMode.RELATIVE, 2),
    0x23: ("BLS", AddressingMode.RELATIVE, 2),
    0x24: ("BCC", AddressingMode.RELATIVE, 2),
    0x25: ("BCS", AddressingMode.RELATIVE, 2),
    0x26: ("BNE", AddressingMode.RELATIVE, 2),
    0x27: ("BEQ", AddressingMode.RELATIVE, 2),
    0x28: ("BVC", AddressingMode.RELATIVE, 2),
    0x29: ("BVS", AddressingMode.RELATIVE, 2),
    0x2A: ("BPL", AddressingMode.RELATIVE, 2),
    0x2B: ("BMI", AddressingMode.RELATIVE, 2),
    0x2C: ("BGE", AddressingMode.RELATIVE, 2),
    0x2D: ("BLT", AddressingMode.RELATIVE, 2),
    0x2E: ("BGT", AddressingMode.RELATIVE, 2),
    0x2F: ("BLE", AddressingMode.RELATIVE, 2),
    # Inherent mode instructions
    0x01: ("NOP", AddressingMode.INHERENT, 1),
    0x06: ("TAP", AddressingMode.INHERENT, 1),
    0x07: ("TPA", AddressingMode.INHERENT, 1),
    0x08: ("INX", AddressingMode.INHERENT, 1),
    0x09: ("DEX", AddressingMode.INHERENT, 1),
    0x0A: ("CLV", AddressingMode.INHERENT, 1),
    0x0B: ("SEV", AddressingMode.INHERENT, 1),
    0x0C: ("CLC", AddressingMode.INHERENT, 1),
    0x0D: ("SEC", AddressingMode.INHERENT, 1),
    0x0E: ("CLI", AddressingMode.INHERENT, 1),
    0x0F: ("SEI", AddressingMode.INHERENT, 1),
    0x10: ("SBA", AddressingMode.INHERENT, 1),
    0x11: ("CBA", AddressingMode.INHERENT, 1),
    0x16: ("TAB", AddressingMode.INHERENT, 1),
    0x17: ("TBA", AddressingMode.INHERENT, 1),
    0x19: ("DAA", AddressingMode.INHERENT, 1),
    0x1B: ("ABA", AddressingMode.INHERENT, 1),
    0x30: ("TSX", AddressingMode.INHERENT, 1),
    0x31: ("INS", AddressingMode.INHERENT, 1),
    0x32: ("PULA", AddressingMode.INHERENT, 1),
    0x33: ("PULB", AddressingMode.INHERENT, 1),
    0x34: ("DES", AddressingMode.INHERENT, 1),
    0x35: ("TXS", AddressingMode.INHERENT, 1),
    0x36: ("PSHA", AddressingMode.INHERENT, 1),
    0x37: ("PSHB", AddressingMode.INHERENT, 1),
    0x38: ("PULX", AddressingMode.INHERENT, 1),
    0x39: ("RTS", AddressingMode.INHERENT, 1),
    0x3A: ("ABX", AddressingMode.INHERENT, 1),
    0x3B: ("RTI", AddressingMode.INHERENT, 1),
    0x3C: ("PSHX", AddressingMode.INHERENT, 1),
    0x3D: ("MUL", AddressingMode.INHERENT, 1),
    0x3E: ("WAI", AddressingMode.INHERENT, 1),
    0x3F: ("SWI", AddressingMode.INHERENT, 1),
    0x40: ("NEGA", AddressingMode.INHERENT, 1),
    0x43: ("COMA", AddressingMode.INHERENT, 1),
    0x44: ("LSRA", AddressingMode.INHERENT, 1),
    0x46: ("RORA", AddressingMode.INHERENT, 1),
    0x47: ("ASRA", AddressingMode.INHERENT, 1),
    0x48: ("ASLA", AddressingMode.INHERENT, 1),
    0x49: ("ROLA", AddressingMode.INHERENT, 1),
    0x4A: ("DECA", AddressingMode.INHERENT, 1),
    0x4C: ("INCA", AddressingMode.INHERENT, 1),
    0x4D: ("TSTA", AddressingMode.INHERENT, 1),
    0x4F: ("CLRA", AddressingMode.INHERENT, 1),
    0x50: ("NEGB", AddressingMode.INHERENT, 1),
    0x53: ("COMB", AddressingMode.INHERENT, 1),
    0x54: ("LSRB", AddressingMode.INHERENT, 1),
    0x56: ("RORB", AddressingMode.INHERENT, 1),
    0x57: ("ASRB", AddressingMode.INHERENT, 1),
    0x58: ("ASLB", AddressingMode.INHERENT, 1),
    0x59: ("ROLB", AddressingMode.INHERENT, 1),
    0x5A: ("DECB", AddressingMode.INHERENT, 1),
    0x5C: ("INCB", AddressingMode.INHERENT, 1),
    0x5D: ("TSTB", AddressingMode.INHERENT, 1),
    0x5F: ("CLRB", AddressingMode.INHERENT, 1),
    # Direct/Indexed/Extended mode memory operations
    0x60: ("NEG", AddressingMode.INDEXED, 2),
    0x63: ("COM", AddressingMode.INDEXED, 2),
    0x64: ("LSR", AddressingMode.INDEXED, 2),
    0x66: ("ROR", AddressingMode.INDEXED, 2),
    0x67: ("ASR", AddressingMode.INDEXED, 2),
    0x68: ("ASL", AddressingMode.INDEXED, 2),
    0x69: ("ROL", AddressingMode.INDEXED, 2),
    0x6A: ("DEC", AddressingMode.INDEXED, 2),
    0x6C: ("INC", AddressingMode.INDEXED, 2),
    0x6D: ("TST", AddressingMode.INDEXED, 2),
    0x6E: ("JMP", AddressingMode.INDEXED, 2),
    0x6F: ("CLR", AddressingMode.INDEXED, 2),
    0x70: ("NEG", AddressingMode.EXTENDED, 3),
    0x73: ("COM", AddressingMode.EXTENDED, 3),
    0x74: ("LSR", AddressingMode.EXTENDED, 3),
    0x76: ("ROR", AddressingMode.EXTENDED, 3),
    0x77: ("ASR", AddressingMode.EXTENDED, 3),
    0x78: ("ASL", AddressingMode.EXTENDED, 3),
    0x79: ("ROL", AddressingMode.EXTENDED, 3),
    0x7A: ("DEC", AddressingMode.EXTENDED, 3),
    0x7C: ("INC", AddressingMode.EXTENDED, 3),
    0x7D: ("TST", AddressingMode.EXTENDED, 3),
    0x7E: ("JMP", AddressingMode.EXTENDED, 3),
    0x7F: ("CLR", AddressingMode.EXTENDED, 3),
}


def format_operand(inst: Instruction, pc: int) -> str:
    """Format operand based on addressing mode."""
    operands = inst.operand_bytes

    if inst.mode == AddressingMode.INHERENT:
        return ""

    if inst.mode == AddressingMode.IMMEDIATE:
        if len(operands) == 1:
            return f"#${operands[0]:02X}"
        if len(operands) == 2:
            return f"#${operands[0]:02X}{operands[1]:02X}"
        return ""

    if inst.mode == AddressingMode.DIRECT:
        if len(operands) >= 1:
            return f"${operands[0]:02X}"
        return ""

    if inst.mode == AddressingMode.EXTENDED:
        if len(operands) >= 2:
            return f"${operands[0]:02X}{operands[1]:02X}"
        return ""

    if inst.mode == AddressingMode.INDEXED:
        if len(operands) >= 1:
            return f"${operands[0]:02X},X"
        return ""

    if inst.mode == AddressingMode.RELATIVE:
        if len(operands) >= 1:
            # Calculate target address (signed offset from PC after instruction)
            offset = operands[0]
            if offset >= 128:
                offset = offset - 256
            target = pc + inst.length + offset
            return f"${target:04X}"

    return ""


def disassemble(data: list[int], start_address: int) -> list[str]:
    """
    Disassemble Motorola 6803 machine code.

    Args:
        data: List of bytes to disassemble
        start_address: Starting address for disassembly

    Returns:
        List of formatted disassembly lines
    """
    lines: list[str] = []
    pc = 0

    while pc < len(data):
        address = start_address + pc
        opcode = data[pc]

        # Look up opcode
        if opcode in OPCODE_TABLE:
            mnemonic, mode, length = OPCODE_TABLE[opcode]

            # Extract operand bytes
            operand_bytes = data[pc + 1 : pc + length]

            # Create instruction
            inst = Instruction(
                address=address,
                opcode=opcode,
                length=length,
                mnemonic=mnemonic,
                mode=mode,
                operand_bytes=operand_bytes,
            )

            # Format hex bytes
            hex_bytes = " ".join(f"{data[pc + i]:02X}" for i in range(length) if pc + i < len(data))

            # Format operand
            operand = format_operand(inst, pc + start_address)

            # Format line
            if operand:
                line = f"{address:04X}: {hex_bytes:<12} {mnemonic:<6} {operand}"
            else:
                line = f"{address:04X}: {hex_bytes:<12} {mnemonic}"

            lines.append(line)
            pc += length

        else:
            # Unknown opcode - display as data byte
            hex_bytes = f"{opcode:02X}"
            line = f"{address:04X}: {hex_bytes:<12} DB     ${opcode:02X}"
            lines.append(line)
            pc += 1

    return lines
