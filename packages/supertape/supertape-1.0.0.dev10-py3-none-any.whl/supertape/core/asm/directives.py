"""Assembler directive processor for M6803 assembler."""

from __future__ import annotations

from supertape.core.asm.errors import DirectiveError
from supertape.core.asm.symbols import SymbolTable


class DirectiveProcessor:
    """
    Process assembler directives.

    Supported directives:
    - ORG $address - Set origin/load address
    - EXC label - Set execution start address
    - DFD $value - Define 16-bit word (big-endian)
    - DB $value - Define 8-bit byte

    FCC/as68 directives:
    - .setcpu <cpu> - Set CPU type (informational, ignored)
    - .code - Switch to code section (no-op for now)
    - .data - Switch to data section (no-op for now)
    - .word <value> - Define 16-bit word (alias for DFD)
    - .byte <value> - Define 8-bit byte (alias for DB)
    - .export <label> - Export symbol (ignored, informational only)
    """

    DEFAULT_ORIGIN = 0x4000  # Default origin for MC-10/Alice

    def __init__(self) -> None:
        """Initialize directive processor."""
        self.origin: int = self.DEFAULT_ORIGIN
        self.exec_address: int | None = None
        self.exec_label: str | None = None  # Store label reference if used
        self.current_section: str = "code"  # Track current section (.code or .data)

    def process_org(self, value: int | str, line: int = 0) -> None:
        """
        Process ORG directive - set origin address.

        Args:
            value: Origin address (must be int)
            line: Line number for error reporting

        Raises:
            DirectiveError: If value is invalid
        """
        if isinstance(value, str):
            raise DirectiveError("ORG", "requires numeric address, not label", line)

        if not isinstance(value, int):
            raise DirectiveError("ORG", "requires numeric address", line)

        if value < 0 or value > 0xFFFF:
            raise DirectiveError("ORG", f"address ${value:X} out of range", line)

        self.origin = value

    def process_exc(self, value: int | str, line: int = 0) -> None:
        """
        Process EXC directive - set execution start address.

        Can be a numeric address or label reference.

        Args:
            value: Execution address (int) or label name (str)
            line: Line number for error reporting

        Raises:
            DirectiveError: If value is invalid
        """
        if isinstance(value, int):
            if value < 0 or value > 0xFFFF:
                raise DirectiveError("EXC", f"address ${value:X} out of range", line)
            self.exec_address = value
            self.exec_label = None

        elif isinstance(value, str):
            # Store label reference to resolve later
            self.exec_label = value
            self.exec_address = None

        else:
            raise DirectiveError("EXC", "requires address or label", line)

    def process_dfd(self, value: int | str, line: int = 0) -> list[int]:
        """
        Process DFD directive - define 16-bit word (big-endian).

        Args:
            value: 16-bit value to store (must be int)
            line: Line number for error reporting

        Returns:
            List of 2 bytes [MSB, LSB] (big-endian)

        Raises:
            DirectiveError: If value is invalid
        """
        if isinstance(value, str):
            raise DirectiveError("DFD", "requires numeric value, not label", line)

        if not isinstance(value, int):
            raise DirectiveError("DFD", "requires numeric value", line)

        if value < 0 or value > 0xFFFF:
            raise DirectiveError("DFD", f"value ${value:X} out of range", line)

        # Return big-endian bytes (MSB first)
        msb = (value >> 8) & 0xFF
        lsb = value & 0xFF
        return [msb, lsb]

    def process_db(self, value: int | str, line: int = 0) -> list[int]:
        """
        Process DB directive - define 8-bit byte.

        Args:
            value: 8-bit value to store (must be int)
            line: Line number for error reporting

        Returns:
            List containing single byte

        Raises:
            DirectiveError: If value is invalid
        """
        if isinstance(value, str):
            raise DirectiveError("DB", "requires numeric value, not label", line)

        if not isinstance(value, int):
            raise DirectiveError("DB", "requires numeric value", line)

        if value < 0 or value > 0xFF:
            raise DirectiveError("DB", f"value ${value:X} out of range", line)

        return [value]

    def get_origin(self) -> int:
        """
        Get the origin address.

        Returns:
            Origin address (defaults to $4000 if not set)
        """
        return self.origin

    def get_exec(self, symbols: SymbolTable | None = None) -> int:
        """
        Get execution start address.

        Args:
            symbols: Symbol table to resolve label references

        Returns:
            Execution address (defaults to origin if not set)

        Raises:
            DirectiveError: If exec label not found in symbol table
        """
        if self.exec_address is not None:
            return self.exec_address

        if self.exec_label is not None:
            if symbols is None:
                raise DirectiveError(
                    "EXC", f"cannot resolve label '{self.exec_label}' without symbol table", 0
                )
            # Resolve label to address
            try:
                return symbols.lookup(self.exec_label)
            except (KeyError, ValueError, AttributeError) as e:
                raise DirectiveError("EXC", f"undefined label '{self.exec_label}'", 0) from e

        # Default to origin
        return self.origin

    def reset(self) -> None:
        """Reset directive processor to initial state."""
        self.origin = self.DEFAULT_ORIGIN
        self.exec_address = None
        self.exec_label = None
        self.current_section = "code"

    # FCC/as68 directive handlers

    def process_setcpu(self, value: int | str, line: int = 0) -> None:
        """
        Process .setcpu directive - informational only, ignored.

        Args:
            value: CPU type (ignored)
            line: Line number for error reporting
        """
        # Informational only - we don't need to do anything
        pass

    def process_code(self, value: int | str, line: int = 0) -> None:
        """
        Process .code directive - switch to code section.

        Args:
            value: Not used
            line: Line number for error reporting
        """
        self.current_section = "code"
        # For now, this is just informational

    def process_data(self, value: int | str, line: int = 0) -> None:
        """
        Process .data directive - switch to data section.

        Args:
            value: Not used
            line: Line number for error reporting
        """
        self.current_section = "data"
        # For now, this is just informational

    def process_word(self, value: int | str, line: int = 0) -> list[int]:
        """
        Process .word directive - alias for DFD.

        Args:
            value: 16-bit value to store
            line: Line number for error reporting

        Returns:
            List of 2 bytes [MSB, LSB] (big-endian)
        """
        return self.process_dfd(value, line)

    def process_byte(self, value: int | str, line: int = 0) -> list[int]:
        """
        Process .byte directive - alias for DB.

        Args:
            value: 8-bit value to store
            line: Line number for error reporting

        Returns:
            List containing single byte
        """
        return self.process_db(value, line)

    def process_export(self, value: int | str, line: int = 0) -> None:
        """
        Process .export directive - informational only, ignored.

        Args:
            value: Symbol name to export (ignored)
            line: Line number for error reporting
        """
        # Informational only - we don't have a linker that uses this
        pass
