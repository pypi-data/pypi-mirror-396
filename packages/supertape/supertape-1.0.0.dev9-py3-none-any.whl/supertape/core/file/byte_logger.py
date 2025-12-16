import logging

from supertape.core.file.api import ByteListener


class ByteLogger(ByteListener):
    def __init__(self) -> None:
        self._logger: logging.Logger = logging.getLogger("file.bytes")

    def process_byte(self, value: int) -> None:
        self._logger.debug(f"{value:02x}")
