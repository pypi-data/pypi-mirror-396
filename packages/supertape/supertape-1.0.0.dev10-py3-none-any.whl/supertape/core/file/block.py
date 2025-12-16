import logging
import string
from collections.abc import Callable

from supertape.core.audio.api import AudioStreamInterruption
from supertape.core.file.api import BlockListener, ByteListener, DataBlock, InvalidBlockType, InvalidCRCError
from supertape.core.log.dump import dump
from supertape.core.output.api import OutputStream
from supertape.core.output.streams import PrintOutputStream

PRINTABLE = [c for c in string.printable if ord(c) > 0x20]

# Block structure constants
# Per TAPE_FORMAT.md: Block = [Type byte, Length byte, Data..., Checksum byte]
BLOCK_HEADER_SIZE = 3  # Type byte + Length byte + Checksum byte


def dump_block(block: DataBlock, callback: Callable[[str], None]) -> None:
    callback("=================================================================================")
    callback(f"Block Type: {block.type:02X}h     Block Size: {len(block.body):02X}h")
    callback("---------------------------------------------------------------------------------")

    for line in dump(block.body):
        callback(line)

    callback("=================================================================================")
    callback("")


class BlockPrinter(BlockListener):
    def __init__(self, stream: OutputStream | None = None) -> None:
        """Initialize the block printer.

        Args:
            stream: Output stream to write to. If None, uses PrintOutputStream.
        """
        self._stream = stream if stream is not None else PrintOutputStream()

    def process_block(self, block: DataBlock) -> None:
        dump_block(block, self._stream.write)


class BlockParser(ByteListener):
    def __init__(self, listeners: list[BlockListener]) -> None:
        self._listeners: list[BlockListener] = listeners
        self._buffer: list[int] | None = None
        self._logger: logging.Logger = logging.getLogger("file.block")

    def process_byte(self, value: int) -> None:
        # self._logger.debug('Current block bytes: %s  Additional byte: %02Xh'
        #                    % (str(['%02Xh' % v for v in self._buffer]) if self._buffer is not None else 'N/A', value))

        if self._buffer is None:
            if value == 0x3C:
                self._buffer = []

        else:
            self._buffer.append(value)

            # Check if we have a complete block: length byte + BLOCK_HEADER_SIZE
            if len(self._buffer) > 1 and len(self._buffer) == self._buffer[1] + BLOCK_HEADER_SIZE:
                block_type: int = self._buffer[0]
                # self._buffer[1] is the length - not used here
                bcrc: int = self._buffer[-1]
                body: list[int] = self._buffer[2:-1]

                if block_type not in [0x00, 0x01, 0xFF]:
                    raise InvalidBlockType(block_type)

                if self._checksum(self._buffer[0:-1]) != bcrc:
                    raise InvalidCRCError()

                block = DataBlock(block_type, body)
                self.log_block(block)

                self._buffer = None

                for listener in self._listeners:
                    listener.process_block(block)

    def process_silence(self) -> None:
        if self._buffer is not None:
            self._buffer = None
            raise AudioStreamInterruption("Unexpected silence while reading block")

    def _checksum(self, bytes: list[int]) -> int:
        return sum(bytes) % 256

    def log_block(self, block: DataBlock) -> None:
        self._logger.debug(
            "================================================================================="
        )
        self._logger.debug(f"Block Type: {block.type:02X}h     Block Size: {len(block.body):02X}h")
        self._logger.debug(
            "---------------------------------------------------------------------------------"
        )

        for line in dump(block.body):
            self._logger.debug(line)

        self._logger.debug(
            "================================================================================="
        )
        self._logger.debug("")


class BlockSerializer(BlockListener):
    def __init__(self, listeners: list[ByteListener]) -> None:
        self._listeners: list[ByteListener] = listeners

    def process_block(self, block: DataBlock) -> None:
        if block.type == 0:
            for listener in self._listeners:
                listener.process_silence()
            for _i in range(128):
                self.notify(0x55)

        self.notify(0x3C)
        self.notify(block.type)
        self.notify(len(block.body))

        for b in block.body:
            self.notify(b)

        self.notify(block.checksum)

        if block.type == 0x00:
            for listener in self._listeners:
                listener.process_silence()
            for _i in range(128):
                self.notify(0x55)
        elif block.type == 0x01:
            self.notify(0x55)
            self.notify(0x55)
        elif block.type == 0xFF:
            self.notify(0x55)
            for listener in self._listeners:
                listener.process_silence()

    def notify(self, b: int) -> None:
        for listener in self._listeners:
            listener.process_byte(b)
