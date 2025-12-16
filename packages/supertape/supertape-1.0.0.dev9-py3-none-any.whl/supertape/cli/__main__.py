#!/usr/bin/env python3
"""
Entry point for supertape command when installed via Poetry.
"""

import sys
from types import ModuleType

from supertape import __version__


def main() -> None:
    """Main entry point for the supertape command."""
    # Handle version flag
    if len(sys.argv) == 2 and sys.argv[1] in ("-v", "--version"):
        print(f"supertape version {__version__}")
        sys.exit(0)

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command: str = sys.argv[1]

    # Map of available commands to their modules
    commands: dict[str, str] = {
        "listen": "supertape.cli.listen",
        "play": "supertape.cli.play",
        "shell": "supertape.cli.shell",
        "devices": "supertape.cli.devices",
        "dump": "supertape.cli.dump",
        "list": "supertape.cli.list",
        "preprocess": "supertape.cli.preprocess",
        "image_to_basic": "supertape.cli.image_to_basic",
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)

    # Import and run the command module
    try:
        module_name: str = commands[command]
        __import__(module_name)
        module: ModuleType = sys.modules[module_name]

        # Remove the command from argv so the module sees clean args
        sys.argv = [sys.argv[0]] + sys.argv[2:]

        # Run the module's main function
        if hasattr(module, "main"):
            module.main()
        else:
            print(f"No main function found in module {module}")
            sys.exit(1)

    except ImportError as e:
        print(f"Error importing command module {command}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error executing command {command}: {e}")
        sys.exit(1)


def print_usage() -> None:
    """Print usage information."""
    print("Usage: supertape <command> [args...]")
    print("       supertape -v | --version")
    print("")
    print("Available commands:")
    print("  listen          - Listen to audio interface or file")
    print("  play            - Play BASIC or assembly source files to audio interface")
    print("  shell           - Interactive tape shell session")
    print("  devices         - List available audio devices")
    print("  dump            - Dump tape file contents")
    print("  list            - List tape file contents in human-readable format")
    print("  preprocess      - Preprocess BASIC files")
    print("  image_to_basic  - Convert images to BASIC")


if __name__ == "__main__":
    main()
