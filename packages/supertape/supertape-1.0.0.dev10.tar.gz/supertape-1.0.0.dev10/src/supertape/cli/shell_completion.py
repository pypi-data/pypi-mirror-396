"""Command completion providers for the enhanced supertape shell."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

from supertape.core.repository.api import TapeFileRepository


class TapeShellCompleter(Completer):
    """Auto-completion provider for the tape shell."""

    def __init__(self, repository: TapeFileRepository) -> None:
        """Initialize the completer with a tape repository."""
        self.repository = repository

        # Core shell commands
        self.commands = {
            "help": "Show help information",
            "exit": "Exit the shell",
            "quit": "Exit the shell",
            "ls": "List tape files",
            "list": "List tape files",
            "play": "Play a tape file",
            "info": "Show detailed file information",
            "remove": "Remove a tape file",
            "rm": "Remove a tape file",
            "clear": "Clear the screen",
            "status": "Show system and audio status",
            "search": "Search tape files",
            "find": "Search tape files",
            "listen": "Start listening to audio input",
            "record": "Start recording from audio input",
            "stop": "Stop audio operations",
        }

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        """Generate completions for the current input."""
        text = document.text_before_cursor
        words = text.split()

        if not words:
            # Complete commands when no input
            for command in self.commands:
                yield Completion(command, start_position=0, display_meta=self.commands[command])
        elif len(words) == 1:
            # Complete commands when typing first word
            word = words[0].lower()
            for command in self.commands:
                if command.startswith(word):
                    yield Completion(command, start_position=-len(word), display_meta=self.commands[command])
        else:
            # Complete file names for commands that take file arguments
            command = words[0].lower()
            if command in ["play", "info", "remove", "rm"]:
                if len(words) >= 2:
                    # Complete tape file names
                    current_word = words[-1] if text.endswith(" ") else words[-1]
                    tape_files = self.repository.get_tape_files()

                    for tape_file in tape_files:
                        if tape_file.fname.lower().startswith(current_word.lower()):
                            yield Completion(
                                tape_file.fname,
                                start_position=-len(current_word),
                                display_meta=f"Type: {self._get_file_type_name(tape_file.ftype)}, Size: {len(tape_file.fbody)} bytes",
                            )
            elif command in ["search", "find"]:
                # For search commands, we could provide suggestions based on existing file names
                if len(words) >= 2:
                    current_word = words[-1] if text.endswith(" ") else words[-1]
                    tape_files = self.repository.get_tape_files()

                    # Suggest unique words from file names
                    unique_words = set()
                    for tape_file in tape_files:
                        for word in tape_file.fname.split():
                            if len(word) > 1:  # Only suggest words longer than 1 character
                                unique_words.add(word.lower())

                    for word in sorted(unique_words):
                        if word.startswith(current_word.lower()):
                            yield Completion(
                                word, start_position=-len(current_word), display_meta="Search term"
                            )

    def _get_file_type_name(self, ftype: int) -> str:
        """Get human-readable file type name."""
        file_type_names = {
            0x00: "BASIC",
            0x01: "DATA",
            0x02: "MACHINE",
            0x05: "ASMSRC",
        }
        return file_type_names.get(ftype, f"0x{ftype:02X}")


class CommandCompleter(Completer):
    """Simple command name completer."""

    def __init__(self, commands: dict[str, str]) -> None:
        """Initialize with a dictionary of commands and their descriptions."""
        self.commands = commands

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        """Generate command completions."""
        text = document.text_before_cursor.lower()

        for command, description in self.commands.items():
            if command.startswith(text):
                yield Completion(command, start_position=-len(text), display_meta=description)


class FileNameCompleter(Completer):
    """File name completer for tape files."""

    def __init__(self, repository: TapeFileRepository) -> None:
        """Initialize with a tape repository."""
        self.repository = repository

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        """Generate file name completions."""
        text = document.text_before_cursor.lower()
        tape_files = self.repository.get_tape_files()

        for tape_file in tape_files:
            if tape_file.fname.lower().startswith(text):
                file_type_name = self._get_file_type_name(tape_file.ftype)
                yield Completion(
                    tape_file.fname,
                    start_position=-len(text),
                    display_meta=f"Type: {file_type_name}, Size: {len(tape_file.fbody)} bytes",
                )

    def _get_file_type_name(self, ftype: int) -> str:
        """Get human-readable file type name."""
        file_type_names = {
            0x00: "BASIC",
            0x01: "DATA",
            0x02: "MACHINE",
            0x05: "ASMSRC",
        }
        return file_type_names.get(ftype, f"0x{ftype:02X}")
