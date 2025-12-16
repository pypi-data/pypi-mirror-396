import argparse
import time
from pathlib import Path
from typing import TextIO

from supertape.core.asm.assembler import M6803Assembler
from supertape.core.asm.encoder import create_machine_file
from supertape.core.assembly.encode import create_assembly_file
from supertape.core.audio.signal_out import AudioPlayerObserver, AudioPlayerProgress
from supertape.core.basic.encode import BasicEncoder, BasicFileCompiler
from supertape.core.basic.minification import minify_basic
from supertape.core.basic.preprocess import preprocess_basic
from supertape.core.c.compiler import compile_c_to_assembly
from supertape.core.c.errors import CCompilerError, FCCNotFoundError
from supertape.core.file.api import TapeFile
from supertape.core.file.play import play_file


def read_program(file: str) -> str:
    f: TextIO
    with open(file) as f:
        basic_source: str = f.read()

    return basic_source


def convert_program_to_tapefile(file_name: str, basic_code: str) -> TapeFile:
    file_compiler: BasicFileCompiler = BasicFileCompiler()
    encoder: BasicEncoder = BasicEncoder()

    instructions = [encoder.encode(line) for line in basic_code.splitlines()]
    outfile: TapeFile = file_compiler.compile_instructions(file_name, instructions)

    return outfile


def convert_assembly_program_to_tapefile(file_name: str, assembly_code: str) -> TapeFile:
    outfile: TapeFile = create_assembly_file(file_name, assembly_code)
    return outfile


def compile_assembly_to_machine(file_name: str, assembly_code: str) -> TapeFile:
    """
    Compile assembly source to MACHINE code.

    Args:
        file_name: Source filename
        assembly_code: Assembly source code

    Returns:
        TapeFile containing compiled machine code
    """
    assembler = M6803Assembler()
    machine_code, load_addr, exec_addr = assembler.assemble(assembly_code)
    return create_machine_file(file_name, machine_code, load_addr, exec_addr)


def compile_c_to_machine(c_source_path: str, cpu: str = "6803") -> tuple[TapeFile, str]:
    """
    Compile C source to MACHINE code via assembly.

    Args:
        c_source_path: Path to C source file
        cpu: Target CPU (6800, 6803, or 6303)

    Returns:
        Tuple of (TapeFile containing compiled machine code, path to generated assembly)

    Raises:
        FCCNotFoundError: If FCC compiler not found
        CCompilerError: If compilation fails
    """
    # Generate assembly path (same directory as C file, .asm extension)
    c_path = Path(c_source_path)
    asm_path = c_path.with_suffix(".asm")

    print(f"Compiling C source: {c_source_path}")

    # Compile C to assembly
    try:
        compile_c_to_assembly(c_path, asm_path, cpu)
        print(f"Generated assembly: {asm_path}")
    except FCCNotFoundError as e:
        print(f"ERROR: {e}")
        raise
    except CCompilerError as e:
        print(f"ERROR: C compilation failed:\n{e}")
        raise

    # Read generated assembly
    with open(asm_path) as f:
        asm_code = f.read()

    print("Assembling to machine code...")

    # Assemble to machine code
    tape_file = compile_assembly_to_machine(str(c_path), asm_code)

    return tape_file, str(asm_path)


class AudioObserver(AudioPlayerObserver):
    def __init__(self) -> None:
        self.complete: bool = False

    def on_progress(self, progress: AudioPlayerProgress) -> None:
        if progress.progress == progress.target:
            self.complete = True

    def wait_for_audio_completion(self) -> None:
        while not self.complete:
            time.sleep(0.5)

        time.sleep(0.5)


def play_tape(device: int | None, tape_file: TapeFile) -> None:
    obs: AudioObserver = AudioObserver()
    play_file(device=device, file=tape_file, observer=obs)
    obs.wait_for_audio_completion()


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Play a local file to the audio interface."
    )
    parser.add_argument("--device", help="Select a device index.", type=int)
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Compile .asm files to MACHINE code instead of ASMSRC",
    )
    parser.add_argument(
        "--cpu",
        choices=["6800", "6803", "6303"],
        default="6803",
        help="Target CPU for C compilation (default: 6803)",
    )
    parser.add_argument("file", type=str)
    args: argparse.Namespace = parser.parse_args()

    tape_file: TapeFile
    if args.file[-4:].lower() == ".bas":
        basic_code: str = read_program(args.file)
        basic_code = preprocess_basic(basic_code)
        basic_code = minify_basic(basic_code)
        tape_file = convert_program_to_tapefile(args.file, basic_code)
    elif args.file[-4:].lower() == ".asm":
        asm_code: str = read_program(args.file)
        if args.compile:
            # Compile to MACHINE code (executable)
            tape_file = compile_assembly_to_machine(args.file, asm_code)
        else:
            # Store as ASMSRC (text)
            tape_file = convert_assembly_program_to_tapefile(args.file, asm_code)
    elif args.file[-2:].lower() == ".c":
        # C source file - compile to MACHINE code
        tape_file, asm_path = compile_c_to_machine(args.file, args.cpu)
        print("Creating MACHINE tape file...")
    else:
        print(f"ERROR: Unsupported file type: {args.file}")
        print("Supported types: .bas, .asm, .c")
        return

    play_tape(device=args.device, tape_file=tape_file)


if __name__ == "__main__":
    main()
