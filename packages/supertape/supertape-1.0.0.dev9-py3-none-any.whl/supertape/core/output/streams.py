"""Output stream implementations for supertape."""

from __future__ import annotations

from prompt_toolkit import print_formatted_text

from supertape.core.output.api import OutputStream


class PrintOutputStream(OutputStream):
    """Output stream that uses standard print() function."""

    def write(self, text: str) -> None:
        """Write text using print().

        Args:
            text: The text to write
        """
        print(text)


class PromptToolkitOutputStream(OutputStream):
    """Output stream that uses prompt_toolkit for thread-safe output.

    This stream is safe to use from background threads while a prompt_toolkit
    prompt is active. It ensures output doesn't interfere with the prompt.
    """

    def write(self, text: str) -> None:
        """Write text using prompt_toolkit's print function.

        Args:
            text: The text to write
        """
        print_formatted_text(text)
