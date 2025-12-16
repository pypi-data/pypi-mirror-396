"""UI components for the enhanced supertape shell."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from supertape.core.file.api import TapeFile


class ShellUI:
    """Rich-based UI components for the supertape shell."""

    def __init__(self) -> None:
        """Initialize the shell UI."""
        self.console = Console()

        # Color scheme for different file types
        self.file_type_colors = {
            0x00: "bright_green",  # BASIC
            0x01: "bright_cyan",  # DATA
            0x02: "bright_red",  # MACHINE
            0x05: "bright_yellow",  # ASMSRC
        }

        self.file_type_names = {
            0x00: "BASIC",
            0x01: "DATA",
            0x02: "MACHINE",
            0x05: "ASMSRC",
        }

    def show_banner(self) -> None:
        """Display the ASCII art banner."""
        banner_art = r"""
   ____  _   _ ____  _____ ____  _____  _    ____  _____
  / ___|| | | |  _ \| ____|  _ \|_   _|/ \  |  _ \| ____|
  \___ \| | | | |_) |  _| | |_) | | | / _ \ | |_) |  _|
   ___) | |_| |  __/| |___|  _ <  | |/ ___ \|  __/| |___
  |____/ \___/|_|   |_____|_| \_\ |_/_/   \_\_|   |_____|

        Audio Tape Emulator for Vintage Computers
        """

        banner_panel = Panel(
            Align.center(Text(banner_art, style="bright_cyan bold")),
            style="bright_blue",
            title="[bold bright_white]Supertape Shell[/bold bright_white]",
            subtitle="[dim]Interactive Tape Management[/dim]",
        )

        self.console.print(banner_panel)
        self.console.print()

    def create_file_table(self, tape_files: list[TapeFile]) -> Table:
        """Create a formatted table of tape files."""
        table = Table(
            title="[bold bright_white]Tape Files[/bold bright_white]",
            show_header=True,
            header_style="bold bright_blue",
            show_lines=True,
            expand=False,
        )

        table.add_column("📁 Name", style="bright_white", width=20)
        table.add_column("📄 Type", style="bright_yellow", width=10)
        table.add_column("📊 Size", style="bright_green", justify="right", width=12)
        table.add_column("🎯 Load Addr", style="bright_magenta", justify="right", width=12)
        table.add_column("🚀 Start Addr", style="bright_cyan", justify="right", width=12)

        if not tape_files:
            table.add_row(
                "[dim]No tape files found[/dim]",
                "[dim]-[/dim]",
                "[dim]-[/dim]",
                "[dim]-[/dim]",
                "[dim]-[/dim]",
            )
        else:
            for tape_file in tape_files:
                file_type = self.file_type_names.get(tape_file.ftype, f"0x{tape_file.ftype:02X}")
                file_type_color = self.file_type_colors.get(tape_file.ftype, "white")

                # Format addresses
                load_addr = f"0x{tape_file.floadaddress:04X}" if tape_file.floadaddress else "-"
                start_addr = f"0x{tape_file.fstartaddress:04X}" if tape_file.fstartaddress else "-"

                table.add_row(
                    f"[bold]{tape_file.fname}[/bold]",
                    f"[{file_type_color}]{file_type}[/{file_type_color}]",
                    f"{len(tape_file.fbody):,} bytes",
                    load_addr,
                    start_addr,
                )

        return table

    def show_file_info(self, tape_file: TapeFile) -> None:
        """Display detailed information about a tape file."""
        file_type = self.file_type_names.get(tape_file.ftype, f"0x{tape_file.ftype:02X}")
        file_type_color = self.file_type_colors.get(tape_file.ftype, "white")

        info_table = Table(show_header=False, box=None, expand=False)
        info_table.add_column("Property", style="bright_blue bold", width=15)
        info_table.add_column("Value", style="bright_white")

        info_table.add_row("📁 Name:", f"[bold]{tape_file.fname}[/bold]")
        info_table.add_row("📄 Type:", f"[{file_type_color}]{file_type}[/{file_type_color}]")
        info_table.add_row("📊 Size:", f"{len(tape_file.fbody):,} bytes")
        info_table.add_row("🔢 Data Type:", f"0x{tape_file.fdatatype:02X}")
        info_table.add_row("📏 Gap:", f"{tape_file.fgap}")
        info_table.add_row(
            "🎯 Load Address:", f"0x{tape_file.floadaddress:04X}" if tape_file.floadaddress else "Not set"
        )
        info_table.add_row(
            "🚀 Start Address:", f"0x{tape_file.fstartaddress:04X}" if tape_file.fstartaddress else "Not set"
        )
        info_table.add_row("🧩 Blocks:", f"{len(tape_file.blocks)}")

        # Show first few bytes as hex preview
        if tape_file.fbody:
            preview_bytes = tape_file.fbody[:16]
            hex_preview = " ".join(f"{b:02X}" for b in preview_bytes)
            if len(tape_file.fbody) > 16:
                hex_preview += "..."
            info_table.add_row("🔍 Preview:", f"[dim]{hex_preview}[/dim]")

        panel = Panel(
            info_table, title="[bold bright_white]File Information[/bold bright_white]", style="bright_blue"
        )

        self.console.print(panel)

    def show_status(
        self, database_name: str | None, database_path: Path, audio_device: int | None, tape_count: int
    ) -> None:
        """Display system status information."""
        status_table = Table(show_header=False, box=None, expand=False)
        status_table.add_column("Property", style="bright_blue bold", width=20)
        status_table.add_column("Value", style="bright_white")

        status_table.add_row("💾 Database:", database_name or "[dim]default[/dim]")
        status_table.add_row("📂 Database Path:", str(database_path))
        status_table.add_row(
            "🔊 Audio Device:", str(audio_device) if audio_device is not None else "[dim]auto[/dim]"
        )
        status_table.add_row("📼 Tape Files:", f"{tape_count}")
        status_table.add_row("💿 Storage Used:", self._get_storage_info(database_path))

        panel = Panel(
            status_table, title="[bold bright_white]System Status[/bold bright_white]", style="bright_green"
        )

        self.console.print(panel)

    def _get_storage_info(self, database_path: Path) -> str:
        """Get storage information for the database directory."""
        try:
            if database_path.exists():
                total_size = sum(f.stat().st_size for f in database_path.rglob("*") if f.is_file())
                if total_size < 1024:
                    return f"{total_size} bytes"
                elif total_size < 1024 * 1024:
                    return f"{total_size / 1024:.1f} KB"
                else:
                    return f"{total_size / (1024 * 1024):.1f} MB"
            return "[dim]0 bytes[/dim]"
        except (OSError, PermissionError):
            return "[dim]unknown[/dim]"

    def show_error(self, message: str) -> None:
        """Display an error message."""
        self.console.print(f"[bold red]❌ Error:[/bold red] {message}")

    def show_success(self, message: str) -> None:
        """Display a success message."""
        self.console.print(f"[bold green]✅ Success:[/bold green] {message}")

    def show_warning(self, message: str) -> None:
        """Display a warning message."""
        self.console.print(f"[bold yellow]⚠️  Warning:[/bold yellow] {message}")

    def show_info(self, message: str) -> None:
        """Display an info message."""
        self.console.print(f"[bold blue]ℹ️  Info:[/bold blue] {message}")

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        self.console.clear()

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print using rich console."""
        self.console.print(*args, **kwargs)
