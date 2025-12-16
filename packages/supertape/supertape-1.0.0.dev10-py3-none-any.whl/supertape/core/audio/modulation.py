import logging
from collections.abc import Sequence

from supertape.core.audio.api import AudioSignalListener, BitListener
from supertape.core.audio.device import AUDIO_TARGET_LEVEL


class AudioModulator(BitListener):
    def __init__(self, listeners: list[AudioSignalListener], rate: int) -> None:
        self._rate: int = rate
        self._listeners: list[AudioSignalListener] = listeners

    def process_bit(self, bit: int) -> None:
        buffer: list[int] = []
        target_level: int = AUDIO_TARGET_LEVEL
        if bit == 0:
            # 1200Hz square wave
            self._generate_samples(buffer, -target_level, self._rate / 1200 / 2)
            self._generate_samples(buffer, target_level, self._rate / 1200 / 2)
        elif bit == 1:
            # 2400Hz square wave
            self._generate_samples(buffer, -target_level, self._rate / 2400 / 2)
            self._generate_samples(buffer, target_level, self._rate / 2400 / 2)
        else:
            raise ValueError(f"Invalid bit value: {bit}, expected 0 or 1")

        for listener in self._listeners:
            listener.process_samples(buffer)

    def process_silence(self) -> None:
        """Process silence event by generating zero-level samples.

        Generates 0.5 seconds of silence (default duration).
        """
        buffer: list[int] = []
        num_samples = int(self._rate * 0.5)
        self._generate_samples(buffer, 0, num_samples)

        for listener in self._listeners:
            listener.process_samples(buffer)

    def _generate_samples(self, buffer: list[int], level: int, samples: float) -> None:
        for _s in range(int(samples)):
            buffer.append(level)


class AudioDemodulator(AudioSignalListener):
    def __init__(self, listeners: list[BitListener], rate: int) -> None:
        self._logger: logging.Logger = logging.getLogger("audio.demodulation")
        # Sample rate
        self._rate: int = rate
        # Timestamp is a counter of samples since creation of the object
        self._ts: int = 0
        # State can be 0 - Silent, 1 - Positive signal
        self._state: int = 0
        # Timestamp the the last status change
        self._state_ts: int = 0
        # Absolute signal threshold in [0:32768[
        self._signal_threshold: int = 3000
        # Bit event listeners
        self._listeners: list[BitListener] = listeners
        # Window buffer for samples storage
        self._window: list[int] = [0, 0, 0, 0, 0, 0]
        # Count consecutive window silences
        self._silences: int = 0

    def process_samples(self, data: Sequence[int]) -> None:
        win: list[int] = self._window

        for sample in data:
            # self._logger.debug('%12d - %s' % (self._ts, ' ' * ((sample + 32768) >> 10) + '+'))

            win.append(sample)
            del win[0]

            delta: int = win[-1] - win[0]

            if delta > self._signal_threshold:
                self._state_ts = self._ts
                self._state = 1
                self._silences = 0
            elif delta < -self._signal_threshold and self._state == 1:
                self._state = 0
                self.register_bit(self._state_ts, self._ts)
                self._silences = 0
            elif abs(win[0]) < self._signal_threshold and abs(win[-1]) < self._signal_threshold:
                self._silences += 1
                self._state = 0
                if self._silences > 10000:
                    self.register_silence()
                    self._silences = 0

            self._ts += 1

    def register_bit(self, first_ts: int, second_ts: int) -> None:
        duration: int = 2 * (second_ts - first_ts)
        freq: float = self._rate / duration
        bitvalue: int = 1 if freq > 1800 else 0
        # self._logger.debug(
        #     'TS: %d / %02.5f Duration=%5d, Freq=%5d, Bit=%d' % (first_ts, first_ts / 44100., duration, freq, bitvalue))
        for listener in self._listeners:
            listener.process_bit(bitvalue)

    def register_silence(self) -> None:
        for listener in self._listeners:
            listener.process_silence()
