import sys
from typing import BinaryIO

from supertape.core.audio.file_in import FileInput
from supertape.core.audio.modulation import AudioDemodulator
from supertape.core.file.api import ByteListener
from supertape.core.file.bytes import ByteDecoder
from supertape.core.log.dump import dump


class ByteListenerStub(ByteListener):
    def __init__(self) -> None:
        self.values: list[int] = []

    def process_byte(self, value: int) -> None:
        self.values.append(value)

    def process_silence(self) -> None:
        """Process silence event - no-op for stub."""
        pass  # Silence is not accumulated


def main() -> None:
    targetfile: str = sys.argv[1]
    byte_accumulator: ByteListenerStub = ByteListenerStub()

    if targetfile[-4:] == ".wav":
        byte_decoder: ByteDecoder = ByteDecoder([byte_accumulator])
        demodulation: AudioDemodulator = AudioDemodulator([byte_decoder], rate=44100)
        file_in: FileInput = FileInput(targetfile, [demodulation])
        file_in.run()

    elif targetfile[-3:] == ".k7":
        tape_file: BinaryIO
        with open(targetfile, "rb") as tape_file:
            while True:
                byte: bytes = tape_file.read(1)

                if len(byte) == 0:
                    break

                byte_accumulator.process_byte(byte[0])

    line: str
    for line in dump(byte_accumulator.values):
        print(line)


if __name__ == "__main__":
    main()
