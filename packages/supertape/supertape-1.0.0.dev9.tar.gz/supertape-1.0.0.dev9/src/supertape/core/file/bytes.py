import logging

from supertape.core.audio.api import BitListener
from supertape.core.file.api import ByteListener

SYNC_BYTE = 0x3C


class ByteDecoder(BitListener):
    def __init__(self, listeners: list[ByteListener]) -> None:
        self._buffer: list[int] = []
        self._listeners: list[ByteListener] = listeners
        self._synchronized: bool = False
        self._logger: logging.Logger = logging.getLogger("decoder.byte")

    def process_bit(self, value: int) -> None:
        # self._logger.debug('Processing bit %d with buffer %s' % (value, str(self._buffer)))
        self._buffer.append(value)

        if len(self._buffer) == 8:
            byte_value: int = sum([self._buffer[i] * pow(2, i) for i in range(0, 8)])

            if not self._synchronized:
                if byte_value == SYNC_BYTE:
                    self._synchronized = True
                else:
                    self._buffer = self._buffer[1:]

            if self._synchronized:
                for listener in self._listeners:
                    listener.process_byte(byte_value)

                self._buffer = []

    def process_silence(self) -> None:
        self._buffer = []
        self._synchronized = False

        for listener in self._listeners:
            listener.process_silence()


class ByteSerializer(ByteListener):
    def __init__(self, listeners: list[BitListener]) -> None:
        self._listeners: list[BitListener] = listeners

    def process_byte(self, byte: int) -> None:
        bits: list[int] = []

        if byte < 0:
            bits.append(byte)
        else:
            for b in range(8):
                bit: int = (byte & (1 << b)) >> b
                bits.append(bit)

        for listener in self._listeners:
            for b in bits:
                listener.process_bit(b)
