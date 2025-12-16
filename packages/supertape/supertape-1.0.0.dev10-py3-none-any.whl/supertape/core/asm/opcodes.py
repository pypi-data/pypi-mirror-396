"""M6803 opcode lookup tables for assembler.

This module provides reverse lookup from (mnemonic, addressing_mode) to opcode bytes.
Built from the disassembler's OPCODE_TABLE.
"""

from __future__ import annotations

from supertape.core.asm.errors import InvalidAddressingModeError, UnknownInstructionError
from supertape.core.disasm.m6803 import OPCODE_TABLE, AddressingMode

# Build reverse lookup table: (mnemonic, mode) -> (opcode, length)
MNEMONIC_TO_OPCODE: dict[tuple[str, AddressingMode], tuple[int, int]] = {}

for opcode, (mnemonic, mode, length) in OPCODE_TABLE.items():
    MNEMONIC_TO_OPCODE[(mnemonic, mode)] = (opcode, length)


def get_opcode(mnemonic: str, mode: AddressingMode, line: int = 0) -> tuple[int, int]:
    """
    Get opcode byte and instruction length for a mnemonic and addressing mode.

    Args:
        mnemonic: Instruction mnemonic (e.g., "LDX", "BRA")
        mode: Addressing mode
        line: Line number for error reporting

    Returns:
        Tuple of (opcode_byte, instruction_length)

    Raises:
        UnknownInstructionError: If mnemonic doesn't exist
        InvalidAddressingModeError: If addressing mode is invalid for this mnemonic
    """
    key = (mnemonic, mode)

    if key not in MNEMONIC_TO_OPCODE:
        # Check if mnemonic exists at all
        valid_modes = get_valid_modes(mnemonic)
        if not valid_modes:
            raise UnknownInstructionError(mnemonic, line)

        # Mnemonic exists but not with this addressing mode
        mode_names = [m.value for m in valid_modes]
        raise InvalidAddressingModeError(mnemonic, mode.value, mode_names, line)

    return MNEMONIC_TO_OPCODE[key]


def get_valid_modes(mnemonic: str) -> list[AddressingMode]:
    """
    Get all valid addressing modes for a given mnemonic.

    Args:
        mnemonic: Instruction mnemonic

    Returns:
        List of valid AddressingMode values for this mnemonic
    """
    modes: list[AddressingMode] = []
    for mn, mode in MNEMONIC_TO_OPCODE.keys():
        if mn == mnemonic and mode not in modes:
            modes.append(mode)
    return modes


def resolve_addressing_mode(mnemonic: str, mode: AddressingMode, value: int, line: int = 0) -> AddressingMode:
    """
    Resolve DIRECT vs EXTENDED addressing mode based on value range.

    For instructions that support both DIRECT and EXTENDED modes, choose:
    - DIRECT if 0 <= value <= 255 and instruction supports DIRECT
    - EXTENDED otherwise

    Args:
        mnemonic: Instruction mnemonic
        mode: Requested addressing mode (DIRECT or EXTENDED)
        value: Operand value
        line: Line number for error reporting

    Returns:
        Resolved AddressingMode (DIRECT or EXTENDED)
    """
    # If not DIRECT or EXTENDED, return as-is
    if mode not in (AddressingMode.DIRECT, AddressingMode.EXTENDED):
        return mode

    valid_modes = get_valid_modes(mnemonic)

    # If value fits in direct page (0-255) and DIRECT is supported, use DIRECT
    if 0 <= value <= 0xFF and AddressingMode.DIRECT in valid_modes and mode == AddressingMode.DIRECT:
        return AddressingMode.DIRECT

    # Otherwise use EXTENDED if available
    if AddressingMode.EXTENDED in valid_modes:
        return AddressingMode.EXTENDED

    # Fallback to requested mode
    return mode


def supports_direct_mode(mnemonic: str) -> bool:
    """
    Check if an instruction supports DIRECT addressing mode.

    Args:
        mnemonic: Instruction mnemonic

    Returns:
        True if DIRECT mode is supported
    """
    return AddressingMode.DIRECT in get_valid_modes(mnemonic)


def supports_extended_mode(mnemonic: str) -> bool:
    """
    Check if an instruction supports EXTENDED addressing mode.

    Args:
        mnemonic: Instruction mnemonic

    Returns:
        True if EXTENDED mode is supported
    """
    return AddressingMode.EXTENDED in get_valid_modes(mnemonic)


def is_branch_instruction(mnemonic: str) -> bool:
    """
    Check if an instruction is a relative branch instruction.

    Args:
        mnemonic: Instruction mnemonic

    Returns:
        True if this is a branch instruction (uses RELATIVE mode)
    """
    return AddressingMode.RELATIVE in get_valid_modes(mnemonic)


def is_inherent_instruction(mnemonic: str) -> bool:
    """
    Check if an instruction uses INHERENT addressing (no operands).

    Args:
        mnemonic: Instruction mnemonic

    Returns:
        True if this is an inherent instruction
    """
    valid_modes = get_valid_modes(mnemonic)
    return len(valid_modes) == 1 and AddressingMode.INHERENT in valid_modes
