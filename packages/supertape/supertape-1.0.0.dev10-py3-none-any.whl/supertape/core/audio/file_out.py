import struct
import wave
from collections.abc import Sequence

import pyaudio

from supertape.core.audio.api import AudioSignalListener
from supertape.core.audio.device import AUDIO_CHANNELS, AUDIO_FORMAT


class FileOutput(AudioSignalListener):
    def __init__(self, filename: str, rate: int = 44100) -> None:
        self._filename: str = filename
        self._wf: wave.Wave_write = wave.open(self._filename, "wb")
        self._wf.setnchannels(AUDIO_CHANNELS)
        self._wf.setframerate(rate)
        self._wf.setsampwidth(2)

        if AUDIO_FORMAT != pyaudio.paInt16:
            raise AssertionError("Unexpected audio format")

    def process_samples(self, buffer: Sequence[int]) -> None:
        format: str = f"{len(buffer):d}h"
        byte_data: bytes = struct.pack(format, *buffer)
        self._wf.writeframes(byte_data)

    def close(self) -> None:
        self._wf.close()
