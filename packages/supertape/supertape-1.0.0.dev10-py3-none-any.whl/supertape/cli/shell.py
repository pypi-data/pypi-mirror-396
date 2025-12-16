"""Enhanced interactive tape shell with rich UI and audio management."""

from __future__ import annotations

import argparse
import shlex
import time
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.progress import Progress, TaskID

from supertape.cli.audio_manager import AudioManager
from supertape.cli.shell_completion import TapeShellCompleter
from supertape.cli.shell_ui import ShellUI
from supertape.core.audio.device import get_device
from supertape.core.audio.signal_out import AudioPlayerObserver, AudioPlayerProgress
from supertape.core.file.api import TapeFile, TapeFileListener
from supertape.core.file.play import play_file
from supertape.core.output.streams import PromptToolkitOutputStream
from supertape.core.repository.api import TapeFileRepository
from supertape.core.repository.dulwich_repo import DulwichRepository


class TapeFileHandler(TapeFileListener):
    """Handles tape files from audio input by adding them to the repository."""

    def __init__(self, repository: TapeFileRepository) -> None:
        """Initialize the tape file handler."""
        self.repository = repository

    def process_file(self, file: TapeFile) -> None:
        """Process a received tape file by adding it to the repository."""
        self.repository.add_tape_file(file)


class PlaybackObserver(AudioPlayerObserver):
    """Observer for audio playback progress with animated progress bar."""

    def __init__(self, progress: Progress, task_id: TaskID) -> None:
        """Initialize the playback observer."""
        self.progress = progress
        self.task_id = task_id
        self.complete = False

    def on_progress(self, progress_info: AudioPlayerProgress) -> None:
        """Handle playback progress updates."""
        if progress_info.target == 0:
            return

        # Update the progress bar with current progress
        self.progress.update(self.task_id, completed=progress_info.progress, total=progress_info.target)

        # Mark as complete when finished
        if progress_info.progress == progress_info.target:
            self.complete = True

    def wait_for_completion(self) -> None:
        """Block until playback completes."""
        while not self.complete:
            time.sleep(0.1)

        # Small delay to ensure clean audio shutdown
        time.sleep(0.5)


class TapeShell:
    """Enhanced interactive tape shell with rich UI and audio management."""

    def __init__(self, repository: TapeFileRepository, audio_device: int | None = None) -> None:
        """Initialize the tape shell."""
        self.repository = repository
        self.audio_manager = AudioManager(repository, audio_device)
        self.ui = ShellUI()
        self.output_stream = PromptToolkitOutputStream()

        # Setup history file
        history_file = Path.home() / ".supertape" / "shell_history"
        history_file.parent.mkdir(parents=True, exist_ok=True)

        # Setup prompt style
        self.prompt_style = Style.from_dict(
            {
                "prompt": "#00aa00 bold",
                "path": "#884444 italic",
                "command": "#aa6600 bold",
            }
        )

        # Setup prompt session with completion and history
        self.session: PromptSession[str] = PromptSession(
            history=FileHistory(str(history_file)),
            completer=TapeShellCompleter(repository),
            style=self.prompt_style,
            complete_while_typing=True,
            auto_suggest=None,
        )

        # Command mapping
        self.commands = {
            "help": self._cmd_help,
            "exit": self._cmd_exit,
            "quit": self._cmd_exit,
            "ls": self._cmd_ls,
            "list": self._cmd_ls,
            "play": self._cmd_play,
            "info": self._cmd_info,
            "remove": self._cmd_remove,
            "rm": self._cmd_remove,
            "clear": self._cmd_clear,
            "status": self._cmd_status,
            "search": self._cmd_search,
            "find": self._cmd_search,
            "listen": self._cmd_listen,
            "record": self._cmd_record,
            "stop": self._cmd_stop,
        }

        self.running = True

    def start(self) -> None:
        """Start the interactive shell."""
        self.ui.show_banner()
        self._show_welcome_message()

        try:
            while self.running:
                try:
                    # Create rich prompt with audio status indicator
                    repo_info = self.repository.get_repository_info()
                    database_name = Path(repo_info.path).name
                    audio_indicator = "🔴" if self.audio_manager.is_listening else "⚫"
                    prompt_text = HTML(
                        f"<prompt>tape</prompt><path>:{database_name}</path> {audio_indicator} <prompt>></prompt> "
                    )

                    # Get user input
                    user_input = self.session.prompt(prompt_text)

                    if user_input.strip():
                        self._execute_command(user_input.strip())

                except KeyboardInterrupt:
                    self.ui.show_info("Use 'exit' or 'quit' to leave the shell")
                    continue
                except EOFError:
                    # Ctrl+D pressed
                    break
        finally:
            # Cleanup audio resources
            self.audio_manager.stop_audio()

        self.ui.show_info("Goodbye! 👋")

    def _show_welcome_message(self) -> None:
        """Show welcome message with basic instructions."""
        repo_info = self.repository.get_repository_info()

        # Get audio device information
        device = get_device()
        if self.audio_manager.device is not None:
            device_info = device.p.get_device_info_by_host_api_device_index(0, self.audio_manager.device)
            device_str = f"Device {self.audio_manager.device}: {device_info['name']}"
        else:
            default_device = device.get_default_device()
            device_info = device.p.get_device_info_by_host_api_device_index(0, default_device)
            device_str = f"Default (Device {default_device}: {device_info['name']})"

        # Show status information
        self.ui.show_success(f"Audio device: {device_str}")
        self.ui.show_success(f"Tape database: {repo_info.file_count} files loaded from {repo_info.path}")
        self.ui.show_info("Type 'help' for commands • 'exit' to quit • 🔴 = listening active")
        self.ui.print()

    def _execute_command(self, command_line: str) -> None:
        """Parse and execute a command."""
        try:
            # Parse command line using shlex for proper quote handling
            parts = shlex.split(command_line)
            if not parts:
                return

            command = parts[0].lower()
            args = parts[1:]

            if command in self.commands:
                self.commands[command](args)
            else:
                self.ui.show_error(f"Unknown command: {command}")
                self.ui.show_info("Type 'help' for available commands")

        except ValueError as e:
            self.ui.show_error(f"Invalid command syntax: {e}")
        except Exception as e:
            self.ui.show_error(f"Command failed: {e}")

    def _cmd_help(self, args: list[str]) -> None:
        """Show help information."""
        if args:
            # Show help for specific command
            command = args[0].lower()
            if command in self.commands:
                self._show_command_help(command)
            else:
                self.ui.show_error(f"No help available for unknown command: {command}")
        else:
            # Show general help
            self._show_general_help()

    def _show_general_help(self) -> None:
        """Show general help with all commands."""
        help_text = """
[bold bright_white]Available Commands:[/bold bright_white]

[bright_green]File Management:[/bright_green]
  [bright_cyan]ls, list[/bright_cyan]           List all tape files
  [bright_cyan]info <file>[/bright_cyan]        Show detailed file information
  [bright_cyan]remove <file>[/bright_cyan]      Remove a tape file
  [bright_cyan]search <pattern>[/bright_cyan]   Search for files by name

[bright_green]Audio Operations:[/bright_green]
  [bright_cyan]listen[/bright_cyan]             Start listening to audio input
  [bright_cyan]record[/bright_cyan]             Start recording from audio input
  [bright_cyan]stop[/bright_cyan]               Stop audio operations

[bright_green]Playback:[/bright_green]
  [bright_cyan]play <file>[/bright_cyan]        Play a tape file to audio output

[bright_green]System:[/bright_green]
  [bright_cyan]status[/bright_cyan]             Show system and audio status
  [bright_cyan]clear[/bright_cyan]              Clear the screen
  [bright_cyan]help [command][/bright_cyan]     Show help (optionally for specific command)
  [bright_cyan]exit, quit[/bright_cyan]         Exit the shell

[bright_yellow]Tips:[/bright_yellow]
  • Use Tab for auto-completion
  • Use arrow keys to navigate command history
  • 🔴 in prompt means audio is actively listening
  • Use quotes for file names with spaces: play "my file.bas"
        """
        self.ui.print(help_text)

    def _show_command_help(self, command: str) -> None:
        """Show help for a specific command."""
        help_info = {
            "ls": "List all tape files in the current database",
            "list": "Alias for ls - list all tape files",
            "info": "Show detailed information about a tape file\nUsage: info <filename>",
            "play": "Play a tape file to the audio output\nUsage: play <filename>",
            "remove": "Remove a tape file from the database\nUsage: remove <filename>",
            "rm": "Alias for remove - remove a tape file",
            "search": "Search for tape files by name pattern\nUsage: search <pattern>",
            "find": "Alias for search - search for tape files",
            "listen": "Start listening to audio input (passive monitoring)",
            "record": "Start recording from audio input to database",
            "stop": "Stop all audio operations (listening and recording)",
            "clear": "Clear the terminal screen",
            "status": "Show system status including database and audio device info",
            "help": "Show help information\nUsage: help [command]",
            "exit": "Exit the tape shell",
            "quit": "Alias for exit - quit the shell",
        }

        if command in help_info:
            self.ui.print(f"[bold bright_white]{command}:[/bold bright_white] {help_info[command]}")
        else:
            self.ui.show_error(f"No help available for: {command}")

    def _cmd_exit(self, args: list[str]) -> None:
        """Exit the shell."""
        self.running = False

    def _cmd_ls(self, args: list[str]) -> None:
        """List tape files."""
        tape_files = self.repository.get_tape_files()
        table = self.ui.create_file_table(tape_files)
        self.ui.print(table)

        if tape_files:
            self.ui.print(f"\n[dim]Total: {len(tape_files)} file(s)[/dim]")

    def _cmd_play(self, args: list[str]) -> None:
        """Play a tape file."""
        if not args:
            self.ui.show_error("Usage: play <filename>")
            return

        filename = args[0]
        tape_files = self.repository.get_tape_files()

        # Find the file
        target_file = None
        for tape_file in tape_files:
            if tape_file.fname.lower() == filename.lower():
                target_file = tape_file
                break

        if target_file is None:
            self.ui.show_error(f"File not found: {filename}")
            self._suggest_similar_files(filename, tape_files)
            return

        # Play the tape file to audio output with animated progress bar
        try:
            with Progress() as progress:
                # Create progress task
                task_id = progress.add_task(f"[cyan]Playing {target_file.fname}...", total=100)

                # Create observer with progress bar
                observer = PlaybackObserver(progress, task_id)

                # Start playback
                play_file(file=target_file, observer=observer, device=self.audio_manager.device)

                # Wait for playback to complete before returning to prompt
                observer.wait_for_completion()

            # Show completion message after progress bar is done
            self.ui.show_success(f"Playback complete: {target_file.fname}")
        except Exception as e:
            self.ui.show_error(f"Playback failed: {e}")

    def _cmd_info(self, args: list[str]) -> None:
        """Show detailed file information."""
        if not args:
            self.ui.show_error("Usage: info <filename>")
            return

        filename = args[0]
        tape_files = self.repository.get_tape_files()

        # Find the file
        target_file = None
        for tape_file in tape_files:
            if tape_file.fname.lower() == filename.lower():
                target_file = tape_file
                break

        if target_file is None:
            self.ui.show_error(f"File not found: {filename}")
            self._suggest_similar_files(filename, tape_files)
            return

        self.ui.show_file_info(target_file)

    def _cmd_remove(self, args: list[str]) -> None:
        """Remove a tape file."""
        if not args:
            self.ui.show_error("Usage: remove <filename>")
            return

        filename = args[0]
        tape_files = self.repository.get_tape_files()

        # Find the file
        target_file = None
        for tape_file in tape_files:
            if tape_file.fname.lower() == filename.lower():
                target_file = tape_file
                break

        if target_file is None:
            self.ui.show_error(f"File not found: {filename}")
            self._suggest_similar_files(filename, tape_files)
            return

        try:
            self.repository.remove_tape_file(target_file)
            self.ui.show_success(f"Removed file: {target_file.fname}")
        except Exception as e:
            self.ui.show_error(f"Failed to remove file: {e}")

    def _cmd_clear(self, args: list[str]) -> None:
        """Clear the screen."""
        self.ui.clear_screen()
        self.ui.show_banner()

    def _cmd_status(self, args: list[str]) -> None:
        """Show system status including audio status."""
        repo_info = self.repository.get_repository_info()
        database_path = Path(repo_info.path)
        db_name = database_path.name

        audio_status = self.audio_manager.get_status()

        # Show regular status
        self.ui.show_status(
            database_name=db_name,
            database_path=database_path,
            audio_device=audio_status["device"],
            tape_count=repo_info.file_count,
        )

        # Show audio status
        self.ui.print("\n[bold bright_white]Audio Status:[/bold bright_white]")
        listening_status = "🔴 Active" if audio_status["listening"] else "⚫ Inactive"
        recording_status = "📼 Recording" if audio_status["recording"] else "📻 Monitoring"

        self.ui.print(f"  Listening: {listening_status}")
        if audio_status["listening"]:
            self.ui.print(f"  Mode: {recording_status}")

    def _cmd_search(self, args: list[str]) -> None:
        """Search for tape files by name pattern."""
        if not args:
            self.ui.show_error("Usage: search <pattern>")
            return

        pattern = args[0].lower()
        tape_files = self.repository.get_tape_files()

        # Find matching files
        matching_files = []
        for tape_file in tape_files:
            if pattern in tape_file.fname.lower():
                matching_files.append(tape_file)

        if matching_files:
            self.ui.print(f"[bold bright_white]Search Results for '{pattern}':[/bold bright_white]")
            table = self.ui.create_file_table(matching_files)
            self.ui.print(table)
            self.ui.print(f"\n[dim]Found {len(matching_files)} matching file(s)[/dim]")
        else:
            self.ui.show_warning(f"No files found matching pattern: {pattern}")

    def _cmd_listen(self, args: list[str]) -> None:
        """Start listening to audio input."""
        if self.audio_manager.is_listening:
            self.ui.show_warning("Audio listening is already active")
            return

        try:
            self.audio_manager.start_listening(output_stream=self.output_stream)
            self.ui.show_success("Started listening to audio input")
            self.ui.show_info("Audio data will be processed and displayed. Use 'stop' to halt.")
        except Exception as e:
            self.ui.show_error(f"Failed to start listening: {e}")

    def _cmd_record(self, args: list[str]) -> None:
        """Start recording from audio input."""
        if self.audio_manager.is_recording:
            self.ui.show_warning("Audio recording is already active")
            return

        try:
            file_handler = TapeFileHandler(self.repository)
            self.audio_manager.start_recording(file_handler, output_stream=self.output_stream)
            self.ui.show_success("Started recording from audio input")
            self.ui.show_info("Received tape files will be automatically saved to the database.")
            self.ui.show_info("Use 'stop' to halt recording.")
        except Exception as e:
            self.ui.show_error(f"Failed to start recording: {e}")

    def _cmd_stop(self, args: list[str]) -> None:
        """Stop all audio operations."""
        if not self.audio_manager.is_listening:
            self.ui.show_warning("No audio operations are currently active")
            return

        try:
            self.audio_manager.stop_audio()
            self.ui.show_success("Stopped all audio operations")
        except Exception as e:
            self.ui.show_error(f"Failed to stop audio operations: {e}")

    def _suggest_similar_files(self, filename: str, tape_files: list[TapeFile]) -> None:
        """Suggest similar file names when a file is not found."""
        filename_lower = filename.lower()
        suggestions = []

        for tape_file in tape_files:
            tape_name_lower = tape_file.fname.lower()

            # Simple similarity check - contains substring or starts with same letter
            if (
                filename_lower in tape_name_lower
                or tape_name_lower in filename_lower
                or (
                    len(filename_lower) > 0
                    and len(tape_name_lower) > 0
                    and filename_lower[0] == tape_name_lower[0]
                )
            ):
                suggestions.append(tape_file.fname)

        if suggestions:
            self.ui.show_info("Did you mean one of these?")
            for suggestion in suggestions[:5]:  # Limit to 5 suggestions
                self.ui.print(f"  • [bright_cyan]{suggestion}[/bright_cyan]")


def main() -> None:
    """Main entry point for the tape shell."""
    parser = argparse.ArgumentParser(description="Run an interactive tape shell session with rich UI.")
    parser.add_argument("--device", help="Select an audio device index.", type=int)
    parser.add_argument("dbname", nargs="?", type=str, help="Name of the tape database to use.")
    args = parser.parse_args()

    # Create repository
    repository = DulwichRepository(args.dbname, observers=[])

    # Start the enhanced shell
    shell = TapeShell(repository, args.device)
    shell.start()


if __name__ == "__main__":
    main()
