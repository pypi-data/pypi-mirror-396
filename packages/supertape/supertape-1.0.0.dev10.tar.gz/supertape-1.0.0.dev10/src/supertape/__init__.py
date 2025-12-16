"""Supertape audio player/recorder software for legacy computers."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("supertape")
except PackageNotFoundError:
    # Fallback for development when package is not installed
    __version__ = "dev"
