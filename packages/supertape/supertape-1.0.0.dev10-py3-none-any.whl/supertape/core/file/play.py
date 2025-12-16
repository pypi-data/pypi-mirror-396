from __future__ import annotations

from supertape.core.audio.api import BitListener
from supertape.core.audio.signal_out import AudioPlayer, AudioPlayerObserver
from supertape.core.file.api import TapeFile
from supertape.core.file.block import BlockSerializer
from supertape.core.file.bytes import ByteSerializer
from supertape.core.file.tapefile import TapeFileSerializer


class _bit_accumulator(BitListener):
    def __init__(self) -> None:
        self.bits: list[int] = []

    def process_bit(self, value: int) -> None:
        self.bits.append(value)

    def process_silence(self) -> None:
        """Process silence event - no-op for bit accumulator."""
        pass  # Silence is handled by audio player, not accumulated


def play_file(file: TapeFile, observer: AudioPlayerObserver, device: int | None = None) -> None:
    bit_accumulator = _bit_accumulator()
    byte_accumulator = ByteSerializer([bit_accumulator])
    block_serializer = BlockSerializer([byte_accumulator])
    tape_serializer = TapeFileSerializer([block_serializer])
    tape_serializer.process_file(file)

    audio_output = AudioPlayer(bit_accumulator.bits, observer, device=device)
    audio_output.start()
