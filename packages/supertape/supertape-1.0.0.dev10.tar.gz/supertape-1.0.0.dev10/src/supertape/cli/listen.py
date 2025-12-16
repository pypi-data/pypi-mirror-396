import argparse

from supertape.core.audio.device import get_device
from supertape.core.audio.file_in import FileInput
from supertape.core.audio.modulation import AudioDemodulator
from supertape.core.audio.signal_in import AudioInput
from supertape.core.basic.decode import BasicDecoder, BasicFileParser
from supertape.core.file.api import ByteListener, TapeFile, TapeFileListener
from supertape.core.file.block import BlockParser, BlockPrinter
from supertape.core.file.bytes import ByteDecoder
from supertape.core.file.tapefile import TapeFileLoader, TapeFilePrinter


class TapeFileLister(TapeFileListener):
    def __init__(self, active: bool) -> None:
        self._active: bool = active

    def process_file(self, file: TapeFile) -> None:
        if self._active:
            parser: BasicFileParser = BasicFileParser()
            decoder: BasicDecoder = BasicDecoder()

            for basic_line in parser.get_binary_instructions(file):
                print("    ", decoder.decode(instruction=basic_line.instruction))


class TapeFileDumper(ByteListener, TapeFileListener):
    def __init__(self, active: bool) -> None:
        self._buffer: list[int] = []
        self._active: bool = active

    def process_byte(self, value: int) -> None:
        if not self._active:
            return

        self._buffer.append(value)

    def process_silence(self) -> None:
        """Process silence event - no-op for dumper."""
        pass  # Silence is not dumped, only actual bytes

    def process_file(self, file: TapeFile) -> None:
        if not self._active:
            return

        print("[", end="")
        ix: int
        b: int
        for ix, b in enumerate(self._buffer):
            if ix > 0:
                print(", ", end="")

            if ix % 16 == 15:
                print("")

            print(f"0x{b:02x}", end="")

        print("]")
        self._buffer = []


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Listen to an audio interface.")
    parser.add_argument("--device", help="Select a device index.", type=int)
    parser.add_argument("--dump", help="Dump raw file bytes.", action="store_true")
    parser.add_argument("--list", help="Show program listing.", action="store_true")
    parser.add_argument("file", nargs="?", type=str)
    args: argparse.Namespace = parser.parse_args()

    file_printer: TapeFilePrinter = TapeFilePrinter()
    block_printer: BlockPrinter = BlockPrinter()
    file_dumper: TapeFileDumper = TapeFileDumper(active=args.dump)
    file_lister: TapeFileLister = TapeFileLister(active=args.list)

    file_loader: TapeFileLoader = TapeFileLoader([file_printer, file_dumper, file_lister])
    block_parser: BlockParser = BlockParser([block_printer, file_loader])
    byte_decoder: ByteDecoder = ByteDecoder([file_dumper, block_parser])

    if args.file is None:
        demodulation: AudioDemodulator = AudioDemodulator([byte_decoder], rate=get_device().get_sample_rate())
        audio_in: AudioInput = AudioInput([demodulation], daemon=False, device=args.device)
        audio_in.start()
    else:
        demodulation_file: AudioDemodulator = AudioDemodulator([byte_decoder], rate=44100)
        file_in: FileInput = FileInput(filename=args.file, listeners=[demodulation_file])
        file_in.run()


if __name__ == "__main__":
    main()
