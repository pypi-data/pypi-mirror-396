import os
from typing import Any

import pyaudio

AUDIO_CHUNKSIZE: int = 2048
AUDIO_FORMAT: int = pyaudio.paInt16
AUDIO_CHANNELS: int = 1

AUDIO_TARGET_LEVEL: int = 25000


class AudioDevice:
    def __init__(self) -> None:
        # Suppress ALSA/JACK errors during PyAudio initialization
        # These errors come from C libraries, so we need to redirect the actual stderr file descriptor
        stderr_fd = 2
        saved_stderr = os.dup(stderr_fd)
        try:
            devnull_fd = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull_fd, stderr_fd)
            os.close(devnull_fd)
            self.p: pyaudio.PyAudio = pyaudio.PyAudio()
        finally:
            os.dup2(saved_stderr, stderr_fd)
            os.close(saved_stderr)

    def __del__(self) -> None:
        self.p.terminate()

    def get_sample_rate(self, device: int | None = None) -> int:
        if device is None:
            device = self.get_default_device()

        device_info: dict[str, Any] = self.p.get_device_info_by_host_api_device_index(0, device)

        # TODO: Remove this hack related to a specific USB audio interface
        if "USB Audio Device: - (hw:" in device_info["name"]:
            return 48000

        sample_rate = device_info.get("defaultSampleRate")
        if sample_rate is None:
            raise ValueError(f"No sample rate found for device {device}")
        return int(sample_rate)

    def open_stream(
        self,
        input: bool | None = None,
        output: bool | None = None,
        input_device_index: int | None = None,
        output_device_index: int | None = None,
        stream_callback: Any | None = None,
    ) -> pyaudio.Stream:
        rate: int = (
            self.get_sample_rate(input_device_index)
            if input_device_index is not None
            else self.get_sample_rate(output_device_index)
        )

        return self.p.open(
            format=AUDIO_FORMAT,
            channels=AUDIO_CHANNELS,
            rate=rate,
            input_device_index=input_device_index,
            output_device_index=output_device_index,
            input=input,
            output=output,
            stream_callback=stream_callback,
            frames_per_buffer=AUDIO_CHUNKSIZE,
        )

    def get_default_device(self) -> int:
        info: dict[str, Any] = self.p.get_host_api_info_by_index(0)
        device_id = info.get("defaultInputDevice")
        if device_id is None:
            raise ValueError("No default input device found")
        return int(device_id)

    def get_audio_devices(self) -> list[list[int | str]]:
        info: dict[str, Any] = self.p.get_host_api_info_by_index(0)
        device_count = info.get("deviceCount")
        if device_count is None:
            raise ValueError("No device count found")
        device_info: list[dict[str, Any]] = [
            self.p.get_device_info_by_host_api_device_index(0, i) for i in range(0, device_count)
        ]

        return [
            [
                d["index"],
                f"{d['name']} (Inputs: {d['maxInputChannels']}, Outputs: {d['maxOutputChannels']})",
            ]
            for d in device_info
        ]


# Suppress verbose ALSA/JACK errors during PyAudio singleton initialization
_device: AudioDevice = AudioDevice()


def get_device() -> AudioDevice:
    return _device
