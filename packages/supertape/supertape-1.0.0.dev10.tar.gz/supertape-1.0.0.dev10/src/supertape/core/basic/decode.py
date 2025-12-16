from collections.abc import Iterator

from supertape.core.basic.instruction import BasicBinaryInstruction
from supertape.core.basic.opcodes import stringify
from supertape.core.file.api import TapeFile


class BasicLine:
    def __init__(self, fileoffset: int, instruction: BasicBinaryInstruction) -> None:
        self.fileoffset: int = fileoffset
        self.instruction: BasicBinaryInstruction = instruction


class BasicFileParser:
    @staticmethod
    def get_binary_instructions(file: TapeFile) -> Iterator[BasicLine]:
        line_offset: int = 0
        line_buffer: list[int] = []

        body: list[int] = file.fbody

        for _offset, byte in enumerate(body):
            line_buffer.append(byte)

            if byte == 0x00 and len(line_buffer) > 4:
                yield BasicLine(fileoffset=line_offset, instruction=BasicBinaryInstruction(bytes=line_buffer))
                line_offset = 0
                line_buffer = []


class BasicDecoder:
    @staticmethod
    def decode(instruction: BasicBinaryInstruction) -> str:
        line_byte_high: int = instruction.bytes[2]
        line_byte_low: int = instruction.bytes[3]
        line_number: int = line_byte_high * 256 + line_byte_low

        text: str = stringify(instruction.bytes[4:])

        return f"{line_number:4d} {text}"
