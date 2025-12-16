import struct
from collections.abc import Sequence
from threading import Thread

from pyaudio import Stream

from supertape.core.audio.api import AudioSignalListener
from supertape.core.audio.device import get_device
from supertape.core.audio.modulation import AudioModulator


class AudioPlayerProgress:
    def __init__(self, progress: int, target: int) -> None:
        self.progress: int = progress
        self.target: int = target

    def __str__(self) -> str:
        return f"{self.progress} out of {self.target}"


class AudioPlayerObserver:
    def on_progress(self, progress: AudioPlayerProgress) -> None:
        pass


class AudioPlayer(Thread):
    def __init__(
        self, bits: list[int], observer: AudioPlayerObserver | None = None, device: int | None = None
    ) -> None:
        if observer is None:
            observer = AudioPlayerObserver()
        super().__init__(daemon=True, name="AudioOutput")
        self._bits: list[int] = bits
        self._observer: AudioPlayerObserver = observer
        self._device: int | None = device

    def run(self) -> None:
        stream: Stream = get_device().open_stream(output_device_index=self._device, input=False, output=True)

        stream_writer: _StreamWriter = _StreamWriter(stream)
        modulator: AudioModulator = AudioModulator(
            [stream_writer], get_device().get_sample_rate(self._device)
        )
        progress: int = 0
        target: int = len(self._bits)

        self._observer.on_progress(AudioPlayerProgress(0, target))

        for bit in self._bits:
            modulator.process_bit(bit)
            progress += 1
            if progress % 20 == 0:
                self._observer.on_progress(AudioPlayerProgress(progress, target))

        self._observer.on_progress(AudioPlayerProgress(target, target))

        stream.stop_stream()
        stream.close()


class _StreamWriter(AudioSignalListener):
    def __init__(self, stream: Stream) -> None:
        self._stream: Stream = stream

    def process_samples(self, buffer: Sequence[int]) -> None:
        format: str = f"{len(buffer):d}h"
        byte_data: bytes = struct.pack(format, *buffer)
        self._stream.write(byte_data)
