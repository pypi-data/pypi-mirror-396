from collections.abc import Sequence

# Short silence: 0.04s
SILENCE_SHORT: int = -1

# Long silence: 0.5s
SILENCE_LONG: int = -2


#####################################################################
# Error management
#####################################################################


class AudioStreamError(BaseException):
    pass


class AudioStreamInterruption(AudioStreamError):
    def __init__(self, reason: str) -> None:
        super().__init__("Audio stream interrupted: " + reason)


#####################################################################
# Event management interfaces
#####################################################################


class AudioSignalListener:
    def process_samples(self, data: Sequence[int]) -> None:
        pass


class AudioLevelListener:
    def process_level(self, level: float) -> None:
        pass


class BitListener:
    def process_bit(self, value: int) -> None:
        pass

    def process_silence(self) -> None:
        pass
