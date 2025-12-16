"""Lexical analyzer for M6803 assembly source code."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Token types for assembly source."""

    LABEL = "label"  # Label definition (e.g., "INIT" or "INIT:")
    MNEMONIC = "mnemonic"  # Instruction mnemonic (e.g., "LDX", "BRA")
    DIRECTIVE = "directive"  # Assembler directive (e.g., "ORG", "EXC", "DFD", "DB")
    IMMEDIATE = "immediate"  # Immediate value (e.g., "#$FF", "#100")
    DIRECT = "direct"  # Direct page address (e.g., "$80")
    EXTENDED = "extended"  # Extended address (e.g., "$4000")
    INDEXED = "indexed"  # Indexed addressing (e.g., "$10,X")
    IDENTIFIER = "identifier"  # Label reference (e.g., "LOOP", "COMPT")
    COMMENT = "comment"  # Comment (;...)
    NEWLINE = "newline"  # End of line
    EOF = "eof"  # End of file


@dataclass
class Token:
    """Represents a lexical token."""

    type: TokenType
    value: str | int
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.value}, {self.value!r}, line={self.line}, col={self.column})"


class Lexer:
    """Tokenize M6803 assembly source code."""

    # Known directives (both supertape and FCC/as68 syntax)
    DIRECTIVES = {
        # Supertape syntax
        "ORG",
        "EXC",
        "DFD",
        "DB",
        # FCC/as68 syntax (with leading dot)
        ".SETCPU",
        ".CODE",
        ".DATA",
        ".WORD",
        ".EXPORT",
        ".BYTE",
    }

    def __init__(self, source: str) -> None:
        """
        Initialize lexer with source code.

        Args:
            source: Assembly source code as string
        """
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def current_char(self) -> str | None:
        """Get current character or None if at end."""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def peek_char(self, offset: int = 1) -> str | None:
        """Peek ahead at character without consuming."""
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]

    def advance(self) -> None:
        """Advance to next character, tracking line and column."""
        if self.pos < len(self.source):
            if self.source[self.pos] == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1

    def skip_whitespace(self) -> None:
        """Skip spaces and tabs (but not newlines)."""
        while self.current_char() in (" ", "\t"):
            self.advance()

    def read_comment(self) -> str:
        """Read comment from ; to end of line."""
        comment = ""
        self.advance()  # Skip ';'
        char = self.current_char()
        while char and char != "\n":
            comment += char
            self.advance()
            char = self.current_char()
        return comment.strip()

    def read_identifier(self) -> str:
        """Read identifier (label or mnemonic), optionally with leading dot for directives."""
        identifier = ""

        # Check for leading dot (for FCC/as68 directives)
        char = self.current_char()
        if char == ".":
            identifier += char
            self.advance()
            char = self.current_char()

        # Read alphanumeric characters and underscore
        while char and (char.isalnum() or char == "_"):
            identifier += char
            self.advance()
            char = self.current_char()

        return identifier.upper()  # Assembly is case-insensitive

    def read_hex_number(self) -> int:
        """Read hexadecimal number after $."""
        self.advance()  # Skip '$'
        hex_str = ""

        char = self.current_char()
        while char and char in "0123456789ABCDEFabcdef":
            hex_str += char
            self.advance()
            char = self.current_char()

        if not hex_str:
            return 0

        return int(hex_str, 16)

    def read_decimal_number(self) -> int:
        """Read decimal number."""
        num_str = ""

        char = self.current_char()
        while char and char.isdigit():
            num_str += char
            self.advance()
            char = self.current_char()

        return int(num_str) if num_str else 0

    def tokenize_operand(self, start_line: int, start_column: int) -> Token | None:
        """
        Tokenize an operand (immediate, direct, extended, indexed, or identifier).

        Returns:
            Token or None if no operand found
        """
        char = self.current_char()

        if char == "#":
            # Immediate addressing: #$FF or #100
            self.advance()  # Skip '#'

            if self.current_char() == "$":
                value = self.read_hex_number()
            else:
                value = self.read_decimal_number()

            return Token(TokenType.IMMEDIATE, value, start_line, start_column)

        elif char == "$":
            # Direct, Extended, or Indexed: $80, $4000, $10,X
            value = self.read_hex_number()

            # Check for indexed mode (,X)
            self.skip_whitespace()
            if self.current_char() == ",":
                self.advance()  # Skip ','
                self.skip_whitespace()
                char = self.current_char()
                if char and char.upper() == "X":
                    self.advance()  # Skip 'X'
                    return Token(TokenType.INDEXED, value, start_line, start_column)

            # Determine DIRECT vs EXTENDED based on value
            if 0 <= value <= 0xFF:
                return Token(TokenType.DIRECT, value, start_line, start_column)
            else:
                return Token(TokenType.EXTENDED, value, start_line, start_column)

        elif char and char.isdigit():
            # Plain decimal number (FCC/as68 syntax): 100, 0,X
            # Could be immediate value, direct, extended, or indexed
            value = self.read_decimal_number()

            # Check for indexed mode (,X)
            self.skip_whitespace()
            if self.current_char() == ",":
                self.advance()  # Skip ','
                self.skip_whitespace()
                char = self.current_char()
                if char and char.upper() == "X":
                    self.advance()  # Skip 'X'
                    return Token(TokenType.INDEXED, value, start_line, start_column)

            # Determine DIRECT vs EXTENDED based on value
            # For plain decimal numbers, treat small values as DIRECT
            if 0 <= value <= 0xFF:
                return Token(TokenType.DIRECT, value, start_line, start_column)
            else:
                return Token(TokenType.EXTENDED, value, start_line, start_column)

        elif char and (char.isalpha() or char == "_" or char == "."):
            # Identifier (label reference) or directive-like reference
            identifier = self.read_identifier()
            return Token(TokenType.IDENTIFIER, identifier, start_line, start_column)

        return None

    def tokenize_line(self) -> list[Token]:
        """Tokenize a single line of assembly."""
        tokens: list[Token] = []
        line_has_leading_whitespace = self.column > 1 or (self.current_char() in (" ", "\t"))

        self.skip_whitespace()

        # Check for empty line or comment-only line
        if self.current_char() in (None, "\n", ";"):
            if self.current_char() == ";":
                comment = self.read_comment()
                tokens.append(Token(TokenType.COMMENT, comment, self.line, self.column))
            if self.current_char() == "\n":
                tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.column))
                self.advance()
            return tokens

        # Check for label at start of line (only if no leading whitespace)
        # Note: Labels cannot start with '.' (that's reserved for directives)
        if not line_has_leading_whitespace and self.current_char() != ".":
            # Look ahead to see if this is a label (identifier followed by whitespace or :)
            saved_pos = self.pos
            saved_line = self.line
            saved_column = self.column

            identifier = self.read_identifier()

            # Check if followed by : or whitespace (indicates label)
            next_char = self.current_char()
            is_label = False

            if next_char == ":":
                self.advance()  # Skip ':'
                is_label = True
            elif next_char in (None, " ", "\t", "\n", ";"):
                is_label = True

            if is_label and identifier:
                tokens.append(Token(TokenType.LABEL, identifier, saved_line, saved_column))
            else:
                # Not a label, restore position and treat as mnemonic/directive
                self.pos = saved_pos
                self.line = saved_line
                self.column = saved_column

        # Skip whitespace before mnemonic/directive
        self.skip_whitespace()

        # Check for mnemonic or directive
        char = self.current_char()
        if char and (char.isalpha() or char == "_" or char == "."):
            start_column = self.column
            identifier = self.read_identifier()

            if identifier in self.DIRECTIVES:
                tokens.append(Token(TokenType.DIRECTIVE, identifier, self.line, start_column))
            else:
                tokens.append(Token(TokenType.MNEMONIC, identifier, self.line, start_column))

        # Skip whitespace before operand
        self.skip_whitespace()

        # Check for operand
        if self.current_char() and self.current_char() not in (";", "\n"):
            operand_token = self.tokenize_operand(self.line, self.column)
            if operand_token:
                tokens.append(operand_token)

        # Skip whitespace before comment
        self.skip_whitespace()

        # Check for comment
        if self.current_char() == ";":
            comment = self.read_comment()
            tokens.append(Token(TokenType.COMMENT, comment, self.line, self.column))

        # Consume newline
        if self.current_char() == "\n":
            tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.column))
            self.advance()

        return tokens

    def tokenize(self) -> list[Token]:
        """
        Tokenize entire source code.

        Returns:
            List of tokens
        """
        self.tokens = []

        while self.pos < len(self.source):
            line_tokens = self.tokenize_line()
            self.tokens.extend(line_tokens)

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))

        return self.tokens
