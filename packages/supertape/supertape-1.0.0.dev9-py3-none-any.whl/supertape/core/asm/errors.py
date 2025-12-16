"""Exception classes for the M6803 assembler."""

from __future__ import annotations


class AssemblerError(Exception):
    """Base exception for all assembler errors."""

    pass


class LexerError(AssemblerError):
    """Exception raised during lexical analysis."""

    def __init__(self, message: str, line: int = 0, column: int = 0) -> None:
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")


class ParserError(AssemblerError):
    """Exception raised during parsing."""

    def __init__(self, message: str, line: int = 0) -> None:
        self.line = line
        super().__init__(f"Line {line}: {message}")


class InvalidLabelError(AssemblerError):
    """Exception raised when a label is invalid (e.g., too long, invalid characters)."""

    def __init__(self, label: str, reason: str, line: int = 0) -> None:
        self.label = label
        self.reason = reason
        self.line = line
        super().__init__(f"Line {line}: Invalid label '{label}': {reason}")


class DuplicateLabelError(AssemblerError):
    """Exception raised when a label is defined multiple times."""

    def __init__(self, label: str, first_line: int, duplicate_line: int) -> None:
        self.label = label
        self.first_line = first_line
        self.duplicate_line = duplicate_line
        super().__init__(
            f"Line {duplicate_line}: Duplicate label '{label}' " f"(first defined at line {first_line})"
        )


class UndefinedLabelError(AssemblerError):
    """Exception raised when a label is referenced but not defined."""

    def __init__(self, label: str, line: int = 0) -> None:
        self.label = label
        self.line = line
        super().__init__(f"Line {line}: Undefined label '{label}'")


class UnknownInstructionError(AssemblerError):
    """Exception raised when an unknown instruction mnemonic is encountered."""

    def __init__(self, mnemonic: str, line: int = 0) -> None:
        self.mnemonic = mnemonic
        self.line = line
        super().__init__(f"Line {line}: Unknown instruction '{mnemonic}'")


class InvalidAddressingModeError(AssemblerError):
    """Exception raised when an invalid addressing mode is used for an instruction."""

    def __init__(self, mnemonic: str, mode: str, valid_modes: list[str], line: int = 0) -> None:
        self.mnemonic = mnemonic
        self.mode = mode
        self.valid_modes = valid_modes
        self.line = line
        modes_str = ", ".join(valid_modes)
        super().__init__(
            f"Line {line}: Invalid addressing mode '{mode}' for instruction '{mnemonic}'. "
            f"Valid modes: {modes_str}"
        )


class BranchOutOfRangeError(AssemblerError):
    """Exception raised when a relative branch target is out of range (-128 to 127)."""

    def __init__(self, mnemonic: str, offset: int, target: int, current: int, line: int = 0) -> None:
        self.mnemonic = mnemonic
        self.offset = offset
        self.target = target
        self.current = current
        self.line = line
        super().__init__(
            f"Line {line}: Branch instruction '{mnemonic}' out of range. "
            f"Target: ${target:04X}, Current: ${current:04X}, Offset: {offset} "
            f"(must be -128 to 127)"
        )


class InvalidOperandError(AssemblerError):
    """Exception raised when an operand is invalid or malformed."""

    def __init__(self, operand: str, reason: str, line: int = 0) -> None:
        self.operand = operand
        self.reason = reason
        self.line = line
        super().__init__(f"Line {line}: Invalid operand '{operand}': {reason}")


class DirectiveError(AssemblerError):
    """Exception raised when a directive has invalid arguments or usage."""

    def __init__(self, directive: str, reason: str, line: int = 0) -> None:
        self.directive = directive
        self.reason = reason
        self.line = line
        super().__init__(f"Line {line}: Directive error in '{directive}': {reason}")
