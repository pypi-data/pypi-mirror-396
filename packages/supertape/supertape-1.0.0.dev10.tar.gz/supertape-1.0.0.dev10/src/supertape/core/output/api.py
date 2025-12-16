"""Output stream interface for supertape."""

from __future__ import annotations

from abc import ABC, abstractmethod


class OutputStream(ABC):
    """Abstract base class for output streams."""

    @abstractmethod
    def write(self, text: str) -> None:
        """Write text to the output stream.

        Args:
            text: The text to write (may include newlines)
        """
        pass
