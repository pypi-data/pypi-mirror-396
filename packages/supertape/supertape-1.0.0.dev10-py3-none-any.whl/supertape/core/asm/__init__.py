"""M6803 assembler module."""

from supertape.core.asm.assembler import M6803Assembler
from supertape.core.asm.encoder import create_machine_file
from supertape.core.asm.errors import (
    AssemblerError,
    BranchOutOfRangeError,
    DirectiveError,
    DuplicateLabelError,
    InvalidAddressingModeError,
    InvalidLabelError,
    InvalidOperandError,
    LexerError,
    ParserError,
    UndefinedLabelError,
    UnknownInstructionError,
)

__all__ = [
    "M6803Assembler",
    "create_machine_file",
    "AssemblerError",
    "LexerError",
    "ParserError",
    "InvalidLabelError",
    "DuplicateLabelError",
    "UndefinedLabelError",
    "UnknownInstructionError",
    "InvalidAddressingModeError",
    "BranchOutOfRangeError",
    "InvalidOperandError",
    "DirectiveError",
]
