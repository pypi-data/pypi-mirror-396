"""C compiler wrapper for FCC (Fuzix Compiler Kit)."""

from __future__ import annotations

import os
import shutil
import subprocess  # nosec B404 - Subprocess needed for C compiler invocation
from pathlib import Path

from supertape.core.c.errors import CCompilationError, FCCNotFoundError


def check_fcc_available() -> bool:
    """
    Check if FCC compiler is available in PATH or default location.

    Returns:
        True if fcc binary is found, False otherwise
    """
    # Check PATH first
    if shutil.which("fcc") is not None:
        return True

    # Check default installation location
    default_fcc = Path("/opt/fcc/bin/fcc")
    return default_fcc.exists() and default_fcc.is_file()


def get_fcc_path() -> str:
    """
    Get path to FCC compiler binary.

    Returns:
        Path to fcc binary

    Raises:
        FCCNotFoundError: If fcc binary is not found
    """
    # Check PATH first
    fcc_path = shutil.which("fcc")
    if fcc_path:
        return fcc_path

    # Check default installation location
    default_fcc = Path("/opt/fcc/bin/fcc")
    if default_fcc.exists() and default_fcc.is_file():
        return str(default_fcc)

    raise FCCNotFoundError()


def compile_c_to_assembly(c_source_path: str | Path, output_asm_path: str | Path, cpu: str = "6803") -> str:
    """
    Compile C source to M6803 assembly using FCC.

    Args:
        c_source_path: Path to .c source file
        output_asm_path: Path where generated .asm file should be saved
        cpu: Target CPU (6800, 6803, or 6303)

    Returns:
        Path to generated assembly file

    Raises:
        FCCNotFoundError: If fcc binary is not found
        CCompilationError: If compilation fails
        FileNotFoundError: If source file doesn't exist
    """
    # Get fcc path (raises FCCNotFoundError if not found)
    fcc_path = get_fcc_path()

    # Convert paths to Path objects
    c_source_path = Path(c_source_path)
    output_asm_path = Path(output_asm_path)

    # Verify source file exists
    if not c_source_path.exists():
        raise FileNotFoundError(f"C source file not found: {c_source_path}")

    # Build fcc command
    # -m<cpu>: Target CPU
    # -S: Compile to assembly only (don't assemble/link)
    # -s: Standalone mode (no OS libraries)
    # -o: Output file
    cmd = [fcc_path, f"-m{cpu}", "-S", "-s", str(c_source_path), "-o", str(output_asm_path)]

    try:
        # Run fcc
        result = subprocess.run(  # nosec B603 - FCC compiler invocation with validated args
            cmd,
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit
        )

        # Check for compilation errors
        if result.returncode != 0:
            # Compilation failed
            error_output = result.stderr if result.stderr else result.stdout
            raise CCompilationError(error_output, result.returncode)

        # Verify output file was created
        if not output_asm_path.exists():
            raise CCompilationError(
                f"FCC did not create output file: {output_asm_path}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}",
                result.returncode,
            )

        return str(output_asm_path)

    except (subprocess.SubprocessError, OSError) as e:
        raise CCompilationError(f"Failed to execute fcc: {e}", -1) from e


def compile_c_to_assembly_text(c_source_code: str, cpu: str = "6803") -> str:
    """
    Compile C source code string to assembly text.

    Creates temporary files for compilation.

    Args:
        c_source_code: C source code as string
        cpu: Target CPU (6800, 6803, or 6303)

    Returns:
        Generated assembly source as string

    Raises:
        FCCNotFoundError: If fcc binary is not found
        CCompilationError: If compilation fails
    """
    import tempfile

    # Create temporary files
    with (
        tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as c_file,
        tempfile.NamedTemporaryFile(mode="w", suffix=".asm", delete=False) as asm_file,
    ):
        c_path = Path(c_file.name)
        asm_path = Path(asm_file.name)

        try:
            # Write C source
            c_file.write(c_source_code)
            c_file.flush()

            # Compile
            compile_c_to_assembly(c_path, asm_path, cpu)

            # Read generated assembly
            with open(asm_path) as f:
                return f.read()

        finally:
            # Clean up temp files
            if c_path.exists():
                os.unlink(c_path)
            if asm_path.exists():
                os.unlink(asm_path)
