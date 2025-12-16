"""Exceptions for C compilation."""

from __future__ import annotations


class CCompilerError(Exception):
    """Base exception for C compilation errors."""

    pass


class FCCNotFoundError(CCompilerError):
    """FCC compiler binary not found in PATH."""

    def __init__(self) -> None:
        super().__init__(
            "FCC compiler not found. Please install Fuzix-Compiler-Kit.\n"
            "Installation instructions:\n"
            "  1. Install Fuzix-Bintools and Fuzix-Compiler-Kit from GitHub\n"
            "  2. Ensure 'fcc' is in your PATH\n"
            "See: https://github.com/EtchedPixels/Fuzix-Compiler-Kit"
        )


class CCompilationError(CCompilerError):
    """C compilation failed."""

    def __init__(self, stderr_output: str, returncode: int) -> None:
        """
        Initialize compilation error.

        Args:
            stderr_output: Error output from FCC
            returncode: Exit code from FCC
        """
        self.stderr = stderr_output
        self.returncode = returncode
        super().__init__(f"C compilation failed (exit code {returncode}):\n{stderr_output}")
