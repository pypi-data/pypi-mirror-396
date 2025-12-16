import logging

from supertape.core.file.api import (
    FILE_TYPE_ASMSRC,
    FILE_TYPE_BASIC,
    FILE_TYPE_DATA,
    FILE_TYPE_MACHINE,
    BlockListener,
    DataBlock,
    TapeFile,
    TapeFileListener,
    UnexpectedBlockType,
)
from supertape.core.output.api import OutputStream
from supertape.core.output.streams import PrintOutputStream

# File type names mapping
FILE_TYPE_NAMES = {
    FILE_TYPE_BASIC: "BASIC",
    FILE_TYPE_MACHINE: "MACHINE",
    FILE_TYPE_DATA: "DATA",
    FILE_TYPE_ASMSRC: "ASMSRC",
}

# Data type names mapping
DATA_TYPE_NAMES = {
    0x00: "binary",
    0xFF: "ASCII",
}

# Gap type names mapping
GAP_TYPE_NAMES = {
    0x00: "none",
    0x01: "continuous",
    0xFF: "gapped",
}


class TapeFilePrinter(TapeFileListener):
    def __init__(self, stream: OutputStream | None = None) -> None:
        """Initialize the tape file printer.

        Args:
            stream: Output stream to write to. If None, uses PrintOutputStream.
        """
        self._stream = stream if stream is not None else PrintOutputStream()

    def process_file(self, file: TapeFile) -> None:
        # Get file type name or use hex if unknown
        type_name = FILE_TYPE_NAMES.get(file.ftype, f"0x{file.ftype:02X}")
        type_display = f"{file.ftype:02X}h ({type_name})"

        # Get data type name
        data_name = DATA_TYPE_NAMES.get(file.fdatatype, f"0x{file.fdatatype:02X}")
        data_display = f"{file.fdatatype:02X}h ({data_name})"

        # Get gap type name
        gap_name = GAP_TYPE_NAMES.get(file.fgap, f"0x{file.fgap:02X}")
        gap_display = f"{file.fgap:02X}h ({gap_name})"

        self._stream.write("  +------------------------\\")
        self._stream.write("  |                        |\\")
        self._stream.write(f"  | File: {file.fname:>8s}         |_\\")
        self._stream.write(f"  | Size: {len(file.fbody):5d} bytes        |")
        self._stream.write(f"  | Type: {type_display:18s} |")
        self._stream.write(f"  | Data: {data_display:18s} |")
        self._stream.write(f"  |  Gap: {gap_display:18s} |")
        self._stream.write("  |                          |")
        self._stream.write("  +--------------------------+")
        self._stream.write("")


class TapeFileLoader(BlockListener):
    def __init__(self, listeners: list[TapeFileListener]) -> None:
        self._listeners: list[TapeFileListener] = listeners
        self._blocks: list[DataBlock] = []
        self._logger: logging.Logger = logging.getLogger("file.tapefile")

    def process_block(self, block: DataBlock) -> None:
        if block.type == 0x00 and len(self._blocks) > 0:
            raise UnexpectedBlockType(block.type, 0)

        if block.type in [0x01, 0xFF] and len(self._blocks) == 0:
            raise UnexpectedBlockType(block.type, 0)

        self._blocks.append(block)

        if block.type == 0xFF:
            file = TapeFile(self._blocks)

            # Get file type name or use hex if unknown
            type_name = FILE_TYPE_NAMES.get(file.ftype, f"0x{file.ftype:02X}")
            type_display = f"{file.ftype:02X}h ({type_name})"

            # Get data type name
            data_name = DATA_TYPE_NAMES.get(file.fdatatype, f"0x{file.fdatatype:02X}")
            data_display = f"{file.fdatatype:02X}h ({data_name})"

            # Get gap type name
            gap_name = GAP_TYPE_NAMES.get(file.fgap, f"0x{file.fgap:02X}")
            gap_display = f"{file.fgap:02X}h ({gap_name})"

            self._logger.debug("  +---------------------\\")
            self._logger.debug("  |                     |\\")
            self._logger.debug(f"  | File: {file.fname:>8s}      |_\\")
            self._logger.debug(f"  | Size: {len(file.fbody):5d} bytes     |")
            self._logger.debug(f"  | Type: {type_display:18s} |")
            self._logger.debug(f"  | Data: {data_display:18s} |")
            self._logger.debug(f"  |  Gap: {gap_display:18s} |")
            self._logger.debug("  |                       |")
            self._logger.debug("  +-----------------------+")

            for listener in self._listeners:
                listener.process_file(file)

            self._blocks = []


class TapeFileSerializer(TapeFileListener):
    def __init__(self, listeners: list[BlockListener]) -> None:
        self._listeners: list[BlockListener] = listeners

    def process_file(self, file: TapeFile) -> None:
        for block in file.blocks:
            for listener in self._listeners:
                listener.process_block(block)
