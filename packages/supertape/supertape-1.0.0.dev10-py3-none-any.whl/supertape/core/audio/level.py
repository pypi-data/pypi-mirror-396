import math
from collections.abc import Sequence

from supertape.core.audio.api import AudioLevelListener, AudioSignalListener


class AudioLevelCalculator(AudioSignalListener):
    def __init__(self, listeners: list[AudioLevelListener]) -> None:
        self._listeners: list[AudioLevelListener] = []
        self.set_listeners(listeners)

    def set_listeners(self, listeners: list[AudioLevelListener]) -> None:
        self._listeners = listeners

    def process_samples(self, bytes: Sequence[int]) -> None:
        levelsum: float = 0
        count: int = len(bytes)

        for byte in bytes:
            level: float = byte / 32768.0
            levelsum += level * level

        levelavg: float = levelsum / count
        levelrms: float = math.sqrt(levelavg)

        for listener in self._listeners:
            listener.process_level(levelrms)
