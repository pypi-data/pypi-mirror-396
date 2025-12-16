"""List tape file contents in human-readable format."""

from __future__ import annotations

import argparse

from supertape.core.audio.file_in import FileInput
from supertape.core.audio.modulation import AudioDemodulator
from supertape.core.basic.decode import BasicDecoder, BasicFileParser
from supertape.core.disasm.m6803 import disassemble
from supertape.core.file.api import (
    FILE_TYPE_ASMSRC,
    FILE_TYPE_BASIC,
    FILE_TYPE_DATA,
    FILE_TYPE_MACHINE,
    TapeFile,
    TapeFileListener,
)
from supertape.core.file.block import BlockParser
from supertape.core.file.bytes import ByteDecoder
from supertape.core.file.load import file_load
from supertape.core.file.tapefile import TapeFileLoader
from supertape.core.log.dump import dump


class TapeFileAccumulator(TapeFileListener):
    """Listener to accumulate a TapeFile from audio processing pipeline."""

    def __init__(self) -> None:
        self.file: TapeFile | None = None

    def process_file(self, file: TapeFile) -> None:
        """Process and store the tape file."""
        self.file = file


def decode_assembly_source(file: TapeFile) -> list[str]:
    """
    Decode assembly source from length-prefixed format.

    Assembly source is stored as:
    [length_byte] + [character bytes] for each line
    Terminated with 0xFF
    """
    lines: list[str] = []
    body = file.fbody
    offset = 0

    while offset < len(body):
        length = body[offset]

        # Check for terminator
        if length == 0xFF:
            break

        offset += 1

        # Check if we have enough bytes
        if offset + length > len(body):
            break

        # Extract line characters
        line_bytes = body[offset : offset + length]
        line = "".join(chr(b) for b in line_bytes)
        lines.append(line)

        offset += length

    return lines


def list_basic(file: TapeFile) -> None:
    """Display BASIC program listing."""
    parser = BasicFileParser()
    decoder = BasicDecoder()

    for basic_line in parser.get_binary_instructions(file):
        print("    ", decoder.decode(instruction=basic_line.instruction))


def list_assembly(file: TapeFile) -> None:
    """Display assembly source listing."""
    lines = decode_assembly_source(file)
    for line in lines:
        print(line)


def list_machine(file: TapeFile) -> None:
    """Display machine code as disassembled 6803 assembly."""
    # Display address information
    if file.fstartaddress is not None:
        print(f"Start Address: ${file.fstartaddress:04X}")
    if file.floadaddress is not None:
        print(f"Load Address:  ${file.floadaddress:04X}")

    # Use load address if available, otherwise use start address
    base_address = file.floadaddress if file.floadaddress is not None else file.fstartaddress

    print("-" * 60)

    # Disassemble the machine code
    disasm_lines = disassemble(file.fbody, base_address)
    for line in disasm_lines:
        print(line)


def list_data(file: TapeFile) -> None:
    """Display data file as hex dump with ASCII."""
    dump_lines = dump(file.fbody)
    for line in dump_lines:
        print(line)


def list_file(file: TapeFile) -> None:
    """Main dispatcher - routes to appropriate display function based on file type."""
    # Print file header
    print(f"File: {file.fname}")

    # Map file type to name
    type_names = {
        FILE_TYPE_BASIC: "BASIC",
        FILE_TYPE_DATA: "DATA",
        FILE_TYPE_MACHINE: "MACHINE",
        FILE_TYPE_ASMSRC: "ASMSRC",
    }

    type_name = type_names.get(file.ftype, f"Unknown (0x{file.ftype:02X})")
    print(f"Type: {type_name}")
    print("-" * 60)

    # Route to appropriate handler
    if file.ftype == FILE_TYPE_BASIC:
        list_basic(file)
    elif file.ftype == FILE_TYPE_ASMSRC:
        list_assembly(file)
    elif file.ftype == FILE_TYPE_MACHINE:
        list_machine(file)
    elif file.ftype == FILE_TYPE_DATA:
        list_data(file)
    else:
        # Unknown file type - default to hex dump
        print(f"Warning: Unknown file type 0x{file.ftype:02X}, displaying as hex dump")
        print()
        list_data(file)


def load_file(filename: str) -> TapeFile:
    """Load tape file from .k7 binary file or .wav audio file."""
    if filename.endswith(".k7"):
        # Load binary tape file directly
        return file_load(filename)

    if filename.endswith(".wav"):
        # Build audio processing pipeline
        accumulator = TapeFileAccumulator()
        file_loader = TapeFileLoader([accumulator])
        block_parser = BlockParser([file_loader])
        byte_decoder = ByteDecoder([block_parser])
        demodulation = AudioDemodulator([byte_decoder], rate=44100)
        file_in = FileInput(filename=filename, listeners=[demodulation])

        # Process the audio file
        file_in.run()

        # Return the accumulated file
        if accumulator.file is None:
            raise ValueError(f"No tape file found in audio file: {filename}")

        return accumulator.file

    # Unsupported file format
    raise ValueError(f"Unsupported file format: {filename}. Expected .k7 or .wav")


def main() -> None:
    """Main entry point for the list command."""
    parser = argparse.ArgumentParser(description="List tape file contents")
    parser.add_argument("file", help="Tape file (.k7) or audio file (.wav) to list")
    args = parser.parse_args()

    try:
        # Load the file
        tape_file = load_file(args.file)

        # Display the file contents
        list_file(tape_file)

    except FileNotFoundError:
        print(f"Error: File not found: {args.file}")
        exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except (OSError, RuntimeError) as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
