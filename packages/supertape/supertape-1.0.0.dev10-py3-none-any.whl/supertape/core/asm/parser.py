"""Parser for M6803 assembly source code.

Converts tokens from the lexer into structured instruction and directive objects.
"""

from __future__ import annotations

from dataclasses import dataclass

from supertape.core.asm.errors import ParserError
from supertape.core.asm.lexer import Token, TokenType
from supertape.core.disasm.m6803 import AddressingMode


@dataclass
class Operand:
    """Represents an instruction operand."""

    mode: AddressingMode
    value: int | str  # int for numeric values, str for label references


@dataclass
class Instruction:
    """Represents a parsed assembly instruction."""

    line_number: int
    label: str | None  # Optional label on this line
    mnemonic: str
    operand: Operand | None


@dataclass
class Directive:
    """Represents an assembler directive."""

    line_number: int
    label: str | None  # Optional label on this line
    directive: str  # "ORG", "EXC", "DFD", "DB"
    value: int | str  # int for numeric values, str for label references


@dataclass
class Program:
    """Represents a complete parsed program."""

    statements: list[Instruction | Directive]


class Parser:
    """Parse tokens into structured instruction and directive objects."""

    def __init__(self, tokens: list[Token]) -> None:
        """
        Initialize parser with token list.

        Args:
            tokens: List of tokens from lexer
        """
        self.tokens = tokens
        self.pos = 0

    def current_token(self) -> Token:
        """Get current token (guaranteed to exist due to EOF token)."""
        return self.tokens[self.pos]

    def peek_token(self, offset: int = 1) -> Token | None:
        """Peek ahead at token without consuming."""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return None
        return self.tokens[pos]

    def advance(self) -> None:
        """Move to next token."""
        if self.pos < len(self.tokens) - 1:  # Don't advance past EOF
            self.pos += 1

    def skip_newlines(self) -> None:
        """Skip over NEWLINE tokens."""
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()

    def parse_operand(self, line_number: int) -> Operand | None:
        """
        Parse an instruction operand from current token.

        Returns:
            Operand object or None if no operand
        """
        token = self.current_token()
        if token.type == TokenType.EOF:
            return None

        if token.type == TokenType.IMMEDIATE:
            self.advance()
            return Operand(mode=AddressingMode.IMMEDIATE, value=token.value)

        elif token.type == TokenType.DIRECT:
            self.advance()
            return Operand(mode=AddressingMode.DIRECT, value=token.value)

        elif token.type == TokenType.EXTENDED:
            self.advance()
            return Operand(mode=AddressingMode.EXTENDED, value=token.value)

        elif token.type == TokenType.INDEXED:
            self.advance()
            return Operand(mode=AddressingMode.INDEXED, value=token.value)

        elif token.type == TokenType.IDENTIFIER:
            # Label reference - could be for branch or other instruction
            # We don't know the addressing mode yet - use EXTENDED as default
            # The assembler will convert to RELATIVE for branch instructions
            self.advance()
            return Operand(mode=AddressingMode.EXTENDED, value=token.value)

        return None

    def parse_directive_operand(self, line_number: int) -> int | str:
        """
        Parse a directive operand (can be numeric or label reference).

        Returns:
            int or str value

        Raises:
            ParserError: If no valid operand found
        """
        token = self.current_token()
        if token.type == TokenType.EOF:
            raise ParserError("Directive requires an operand", line_number)

        if token.type in (
            TokenType.IMMEDIATE,
            TokenType.DIRECT,
            TokenType.EXTENDED,
            TokenType.INDEXED,
        ):
            self.advance()
            return int(token.value)

        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return str(token.value)

        raise ParserError(f"Invalid directive operand: {token.type.value}", line_number)

    def parse_line(self) -> Instruction | Directive | None:
        """
        Parse a single line (instruction or directive).

        Returns:
            Instruction, Directive, or None for empty/comment lines
        """
        # Skip comments and newlines
        while self.current_token().type in (TokenType.COMMENT, TokenType.NEWLINE):
            self.advance()

        # Check for EOF
        if self.current_token().type == TokenType.EOF:
            return None

        # Track current line number
        line_number = self.current_token().line

        # Check for label
        label: str | None = None
        if self.current_token().type == TokenType.LABEL:
            label = str(self.current_token().value)
            self.advance()

        # Skip whitespace/comments after label
        while self.current_token().type == TokenType.COMMENT:
            self.advance()

        # Check for directive or mnemonic
        token = self.current_token()
        if token.type in (TokenType.NEWLINE, TokenType.EOF):
            # Label-only line
            if label:
                # Create a pseudo-directive for label-only lines
                # We'll handle this as a special case in the assembler
                return Directive(
                    line_number=line_number,
                    label=label,
                    directive="LABEL",
                    value=0,
                )
            return None

        if token.type == TokenType.DIRECTIVE:
            directive_name = str(token.value)
            self.advance()

            # Parse directive operand
            value: int | str = 0
            if self.current_token().type not in (
                TokenType.COMMENT,
                TokenType.NEWLINE,
                TokenType.EOF,
            ):
                value = self.parse_directive_operand(line_number)

            return Directive(
                line_number=line_number,
                label=label,
                directive=directive_name,
                value=value,
            )

        elif token.type == TokenType.MNEMONIC:
            mnemonic = str(token.value)
            self.advance()

            # Parse operand if present
            operand: Operand | None = None
            if self.current_token().type not in (
                TokenType.COMMENT,
                TokenType.NEWLINE,
                TokenType.EOF,
            ):
                operand = self.parse_operand(line_number)

            return Instruction(line_number=line_number, label=label, mnemonic=mnemonic, operand=operand)

        # Label-only line (label followed by newline/comment)
        if label:
            return Directive(line_number=line_number, label=label, directive="LABEL", value=0)

        return None

    def parse(self) -> Program:
        """
        Parse all tokens into a program.

        Returns:
            Program object containing all instructions and directives
        """
        statements: list[Instruction | Directive] = []

        while self.pos < len(self.tokens):
            # Check for EOF before parsing
            if self.current_token().type == TokenType.EOF:
                break

            statement = self.parse_line()
            if statement:
                statements.append(statement)

            # Safety check: if we haven't advanced, break to prevent infinite loop
            if self.current_token().type == TokenType.EOF:
                break

        return Program(statements=statements)
