"""Encoder to create MACHINE TapeFile from assembled machine code."""

from __future__ import annotations

import os

from supertape.core.file.api import (
    FILE_DATA_TYPE_BIN,
    FILE_GAP_NONE,
    FILE_TYPE_MACHINE,
    DataBlock,
    TapeFile,
)


def cleanup_program_name(filename: str) -> str:
    """
    Extract and clean program name from filename.

    Args:
        filename: Full file path

    Returns:
        Cleaned program name (max 8 chars, uppercase)
    """
    base_name: str = os.path.split(filename)[-1]
    program_name: str = os.path.splitext(base_name)[0]

    if len(program_name) > 8:
        program_name = program_name[0:8]

    program_name = program_name.upper()
    return program_name


def create_machine_file(
    filename: str, machine_code: list[int], load_address: int, exec_address: int
) -> TapeFile:
    """
    Create a MACHINE (0x02) type TapeFile from assembled machine code.

    Args:
        filename: Source filename (used for tape file name)
        machine_code: List of machine code bytes
        load_address: Address where code should be loaded
        exec_address: Address where execution should start

    Returns:
        TapeFile object ready to be written to audio or .k7 file

    Note:
        CRITICAL: Tape file headers use LITTLE-ENDIAN byte order for addresses!
        This is different from M6803 machine code which uses BIG-ENDIAN.
    """
    # Clean up filename (max 8 chars)
    program_name = cleanup_program_name(filename)
    filename_bytes: list[int] = [
        ord(program_name[i]) if i < len(program_name) else ord(" ") for i in range(8)
    ]

    # Create header block (type 0x00)
    # Tape format uses LITTLE-ENDIAN for addresses in header!
    exec_low = exec_address & 0xFF
    exec_high = (exec_address >> 8) & 0xFF
    load_low = load_address & 0xFF
    load_high = (load_address >> 8) & 0xFF

    head: DataBlock = DataBlock(
        type=0x00,
        body=filename_bytes
        + [
            FILE_TYPE_MACHINE,  # [8] file type (0x02 = MACHINE)
            FILE_DATA_TYPE_BIN,  # [9] binary data (not ASCII)
            FILE_GAP_NONE,  # [10] continuous blocks (no gaps)
            exec_low,  # [11] exec address low byte (little-endian!)
            exec_high,  # [12] exec address high byte
            load_low,  # [13] load address low byte (little-endian!)
            load_high,  # [14] load address high byte
        ],
    )

    # Create data blocks (type 0x01) - max 255 bytes per block
    blocks: list[DataBlock] = [head]
    body = machine_code.copy()

    while body:
        block_content: list[int] = body[:255]
        body = body[len(block_content) :]
        blocks.append(DataBlock(type=0x01, body=block_content))

    # Create footer block (type 0xFF)
    foot: DataBlock = DataBlock(type=0xFF, body=[])
    blocks.append(foot)

    return TapeFile(blocks=blocks)
