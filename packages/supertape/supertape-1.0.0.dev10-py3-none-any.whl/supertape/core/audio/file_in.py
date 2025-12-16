import struct
import wave

from supertape.core.audio.api import AudioSignalListener
from supertape.core.audio.device import AUDIO_CHUNKSIZE


class FileInput:
    def __init__(self, filename: str, listeners: list[AudioSignalListener]) -> None:
        self._signallisteners: list[AudioSignalListener] = listeners
        self._filename: str = filename

    def run(self) -> None:
        wf: wave.Wave_read = wave.open(self._filename, "rb")

        # Get WAV file properties
        sample_width: int = wf.getsampwidth()  # 1 = 8-bit, 2 = 16-bit
        channels: int = wf.getnchannels()  # 1 = mono, 2 = stereo

        # Determine struct format based on sample width
        # 8-bit PCM is unsigned (0-255), 16-bit PCM is signed
        if sample_width == 1:
            format_char = "B"  # unsigned char (8-bit)
        elif sample_width == 2:
            format_char = "h"  # signed short (16-bit)
        else:
            raise ValueError(f"Unsupported sample width: {sample_width} bytes")

        while True:
            block = wf.readframes(AUDIO_CHUNKSIZE)

            # Calculate number of samples in block
            bytes_per_sample = sample_width * channels
            if len(block) % bytes_per_sample != 0:
                # Trim incomplete frame
                block = block[: -(len(block) % bytes_per_sample)]

            num_samples = len(block) // sample_width
            if num_samples == 0:
                break

            # Unpack all samples
            format: str = f"{num_samples}{format_char}"
            all_samples: tuple[int, ...] = struct.unpack(format, block)

            # Convert 8-bit unsigned (0-255) to signed and scale to 16-bit range
            # AudioDemodulator expects 16-bit range (-32768 to 32767) with threshold of 3000
            if sample_width == 1:
                all_samples = tuple((v - 128) * 256 for v in all_samples)

            # If stereo, extract only left channel (every channels-th sample)
            if channels == 1:
                samples = all_samples
            else:
                samples = all_samples[::channels]  # Take every Nth sample

            for listener in self._signallisteners:
                listener.process_samples(samples)

        wf.close()
