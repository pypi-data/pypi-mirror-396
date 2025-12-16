from abc import ABC, abstractmethod
from collections.abc import Sequence

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


class AudioSignalListener(ABC):
    """Abstract base class for audio signal event listeners."""

    @abstractmethod
    def process_samples(self, data: Sequence[int]) -> None:
        """Process audio samples.

        Args:
            data: Sequence of audio sample values
        """
        pass


class AudioLevelListener(ABC):
    """Abstract base class for audio level event listeners."""

    @abstractmethod
    def process_level(self, level: float) -> None:
        """Process audio level.

        Args:
            level: Audio level value
        """
        pass


class BitListener(ABC):
    """Abstract base class for bit event listeners."""

    @abstractmethod
    def process_bit(self, value: int) -> None:
        """Process a bit value.

        Args:
            value: The bit value (0 or 1)
        """
        pass

    @abstractmethod
    def process_silence(self) -> None:
        """Process a silence event."""
        pass
