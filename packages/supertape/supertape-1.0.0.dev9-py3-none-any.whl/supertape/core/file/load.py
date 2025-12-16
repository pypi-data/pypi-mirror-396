from __future__ import annotations

from typing import BinaryIO

from supertape.core.file.api import TapeFile, TapeFileListener
from supertape.core.file.block import BlockParser
from supertape.core.file.tapefile import TapeFileLoader


class _filelistener(TapeFileListener):
    def __init__(self) -> None:
        self.file: TapeFile | None = None

    def process_file(self, file: TapeFile) -> None:
        self.file = file


def _load_from_stream(stream: BinaryIO) -> TapeFile:
    """Load a TapeFile from a binary stream.

    Args:
        stream: Binary stream to read .k7 file data from

    Returns:
        TapeFile object loaded from the stream

    Raises:
        ValueError: If no tape file was loaded from the stream
    """
    file_listener = _filelistener()
    tape_file_loader = TapeFileLoader([file_listener])
    block_parser = BlockParser([tape_file_loader])

    while True:
        byte: bytes = stream.read(1)

        if len(byte) == 0:
            break

        block_parser.process_byte(byte[0])

    if file_listener.file is None:
        raise ValueError("No tape file was loaded")
    return file_listener.file


def file_load(file_name: str | BinaryIO) -> TapeFile:
    """Load a TapeFile from a file path or binary stream.

    Args:
        file_name: Either a file path (str) or a binary stream (BinaryIO)

    Returns:
        TapeFile object loaded from the file or stream

    Raises:
        ValueError: If no tape file was loaded
    """
    if isinstance(file_name, str):
        with open(file_name, "rb") as tape_file:
            return _load_from_stream(tape_file)
    else:
        return _load_from_stream(file_name)
