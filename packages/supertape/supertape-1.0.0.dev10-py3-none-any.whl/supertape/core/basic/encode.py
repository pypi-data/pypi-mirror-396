import os
import re
from re import Pattern

from supertape.core.basic.instruction import BasicBinaryInstruction
from supertape.core.basic.opcodes import binarize
from supertape.core.file.api import DataBlock, TapeFile


class BasicEncoder:
    def __init__(self) -> None:
        self._basicindex: int = 0x3346
        self.re_line: Pattern[str] = re.compile(r"^\s*(\d+)\s*(.*\S)\s*$")

    def encode(self, basicline: str) -> BasicBinaryInstruction:
        bytes: list[int] = []

        for lno, linst in self.re_line.findall(basicline):
            bin_insruction: list[int] = binarize(linst)
            self._basicindex += 4 + len(bin_insruction)

            lno_int: int = int(lno)
            bytes.append((self._basicindex & 0xFF00) >> 8)
            bytes.append(self._basicindex & 0x00FF)
            bytes.append(int(lno_int / 256))
            bytes.append(lno_int % 256)
            bytes += bin_insruction

        return BasicBinaryInstruction(bytes=bytes)


class BasicFileCompiler:
    @staticmethod
    def cleanup_program_name(filename: str) -> str:
        base_name: str = os.path.split(filename)[-1]
        program_name: str = os.path.splitext(base_name)[0]

        if len(program_name) > 8:
            program_name = program_name[0:8]

        program_name = program_name.upper()
        return program_name

    @staticmethod
    def compile_instructions(filename: str, lines: list[BasicBinaryInstruction]) -> TapeFile:
        body: list[int] = []

        filename = BasicFileCompiler.cleanup_program_name(filename)
        filename_bytes: list[int] = [ord(filename[i]) if i < len(filename) else 0 for i in range(8)]

        for instruction in lines:
            body += instruction.bytes

        body += [0x00, 0x00]

        head: DataBlock = DataBlock(
            type=0x00,
            body=filename_bytes
            + [
                0x00,  # [8] file type (BASIC)
                0x00,  # [9] ASCII flag (binary/tokenized)
                0xFF,  # [10] gap flag (gapped - standard for BASIC)
                0x00,  # [11] start address low byte (unused for BASIC)
                0x00,  # [12] start address high byte (unused for BASIC)
                0x00,  # [13] load address low byte (unused for BASIC)
                0x00,  # [14] load address high byte (unused for BASIC)
            ],
        )

        foot: DataBlock = DataBlock(type=0xFF, body=[])

        blocks: list[DataBlock] = [head]

        while body:
            block_content: list[int] = body[:255]
            body = body[len(block_content) :]

            blocks.append(DataBlock(type=0x01, body=block_content))

        blocks.append(foot)

        return TapeFile(blocks=blocks)
