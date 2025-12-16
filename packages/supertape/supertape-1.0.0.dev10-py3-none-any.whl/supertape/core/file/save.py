"""Save TapeFile objects to .k7 binary files."""

from __future__ import annotations

from supertape.core.file.api import ByteListener, TapeFile
from supertape.core.file.block import BlockSerializer
from supertape.core.file.tapefile import TapeFileSerializer


class _ByteCollector(ByteListener):
    """Collects bytes from serialization pipeline."""

    def __init__(self) -> None:
        self.bytes: list[int] = []

    def process_byte(self, value: int) -> None:
        """Process a byte from the serialization pipeline.

        Args:
            value: Byte value to process (must be 0-255)
        """
        self.bytes.append(value)

    def process_silence(self) -> None:
        """Process silence marker (no-op for file storage)."""
        pass


def file_save(filename: str, tape: TapeFile) -> None:
    """Save a TapeFile to a .k7 binary file.

    This function is the inverse of file_load(). It serializes a TapeFile
    object to the .k7 binary format used by emulators and cassette storage.

    The serialization pipeline:
    TapeFile → TapeFileSerializer → BlockSerializer → _ByteCollector → bytes → file

    Args:
        filename: Path to the .k7 file to create
        tape: TapeFile object to save

    Raises:
        OSError: If file cannot be written
        IOError: If file I/O operation fails
    """
    # Create byte collector
    collector = _ByteCollector()

    # Build serialization pipeline: TapeFile → Blocks → Bytes
    serializer = BlockSerializer([collector])
    file_serializer = TapeFileSerializer([serializer])

    # Serialize the file
    file_serializer.process_file(tape)

    # Write bytes to disk
    with open(filename, "wb") as f:
        f.write(bytes(collector.bytes))
