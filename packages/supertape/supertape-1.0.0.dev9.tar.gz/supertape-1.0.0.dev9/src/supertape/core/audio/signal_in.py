import logging
import struct
import time
from threading import Thread

import pyaudio

from supertape.core.audio.api import AudioSignalListener, AudioStreamError
from supertape.core.audio.device import get_device


class AudioInput(Thread):
    def __init__(
        self, listeners: list[AudioSignalListener], daemon: bool = True, device: int | None = None
    ) -> None:
        super().__init__(daemon=daemon, name="AudioInput")
        self._logger: logging.Logger = logging.getLogger("audio.in")
        self._active: bool = True
        self._signallisteners: list[AudioSignalListener] = listeners
        self._device: int | None = device

    def set_listeners(self, listeners: list[AudioSignalListener]) -> None:
        self._signallisteners = listeners

    def run(self) -> None:
        self._logger.info("Scanning audio input")

        stream: pyaudio.Stream = get_device().open_stream(
            input_device_index=self._device, input=True, output=False, stream_callback=self.callback
        )

        stream.start_stream()

        while self._active and stream.is_active():
            time.sleep(1)

        stream.stop_stream()
        stream.close()

    def stop(self) -> None:
        self._active = False

    def callback(
        self, in_data: bytes, frame_count: int, time_info: dict[str, float], status: int
    ) -> tuple[bytes, int]:
        if status != 0:
            self._logger.debug(f"Audio stream status {status}: {frame_count} frames, timing={time_info}")

        format: str = f"{frame_count:d}h"
        bytes: tuple[int, ...] = struct.unpack(format, in_data)

        for listener in self._signallisteners:
            try:
                listener.process_samples(bytes)
            except AudioStreamError as e:
                self._logger.warning(e)

        return (in_data, pyaudio.paContinue)
