"""Symbol table management for M6803 assembler."""

from __future__ import annotations

from supertape.core.asm.errors import DuplicateLabelError, InvalidLabelError, UndefinedLabelError


class SymbolTable:
    """
    Symbol table for tracking label definitions and references.

    M6803 assembly labels have these constraints:
    - Maximum 5 characters
    - Alphanumeric and underscore only
    - Must start with letter or underscore
    """

    MAX_LABEL_LENGTH = 5

    def __init__(self) -> None:
        """Initialize empty symbol table."""
        self.symbols: dict[str, int] = {}
        self.definitions: dict[str, int] = {}  # Track line where label was defined

    def _validate_label(self, label: str, line: int = 0) -> None:
        """
        Validate label syntax.

        Args:
            label: Label name to validate
            line: Line number for error reporting

        Raises:
            InvalidLabelError: If label is invalid
        """
        # Check length
        if len(label) > self.MAX_LABEL_LENGTH:
            raise InvalidLabelError(label, f"exceeds maximum length of {self.MAX_LABEL_LENGTH}", line)

        if len(label) == 0:
            raise InvalidLabelError(label, "label cannot be empty", line)

        # Check first character
        if not (label[0].isalpha() or label[0] == "_"):
            raise InvalidLabelError(label, "must start with letter or underscore", line)

        # Check all characters
        for char in label:
            if not (char.isalnum() or char == "_"):
                raise InvalidLabelError(label, f"contains invalid character '{char}'", line)

    def define(self, label: str, address: int, line: int = 0) -> None:
        """
        Define a label at a given address.

        Args:
            label: Label name
            address: Memory address for this label
            line: Line number where label is defined

        Raises:
            InvalidLabelError: If label syntax is invalid
            DuplicateLabelError: If label already defined
        """
        # Validate label syntax
        self._validate_label(label, line)

        # Check for duplicate
        if label in self.symbols:
            first_line = self.definitions[label]
            raise DuplicateLabelError(label, first_line, line)

        # Define the label
        self.symbols[label] = address
        self.definitions[label] = line

    def lookup(self, label: str, line: int = 0) -> int:
        """
        Look up the address of a label.

        Args:
            label: Label name to look up
            line: Line number for error reporting

        Returns:
            Memory address of the label

        Raises:
            UndefinedLabelError: If label not defined
        """
        if label not in self.symbols:
            raise UndefinedLabelError(label, line)

        return self.symbols[label]

    def is_defined(self, label: str) -> bool:
        """
        Check if a label is defined.

        Args:
            label: Label name to check

        Returns:
            True if label is defined, False otherwise
        """
        return label in self.symbols

    def get_all(self) -> dict[str, int]:
        """
        Get all defined labels and their addresses.

        Returns:
            Dictionary mapping label names to addresses
        """
        return self.symbols.copy()

    def clear(self) -> None:
        """Clear all symbols from the table."""
        self.symbols.clear()
        self.definitions.clear()
