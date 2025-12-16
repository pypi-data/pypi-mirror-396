"""Audio management for the supertape shell."""

from __future__ import annotations

from typing import Any

from supertape.core.audio.modulation import AudioDemodulator
from supertape.core.audio.signal_in import AudioInput
from supertape.core.file.api import TapeFileListener
from supertape.core.file.block import BlockParser, BlockPrinter
from supertape.core.file.bytes import ByteDecoder
from supertape.core.file.tapefile import TapeFileLoader, TapeFilePrinter
from supertape.core.output.api import OutputStream
from supertape.core.repository.api import TapeFileRepository


class AudioManager:
    """Manages audio operations for the tape shell."""

    def __init__(self, repository: TapeFileRepository, device: int | None = None) -> None:
        """Initialize the audio manager."""
        self.repository = repository
        self.device = device
        self.audio_in: AudioInput | None = None
        self.is_listening = False
        self.is_recording = False

    def start_listening(
        self, file_handler: TapeFileListener | None = None, output_stream: OutputStream | None = None
    ) -> None:
        """Start listening to audio input.

        Args:
            file_handler: Optional handler for received tape files
            output_stream: Optional output stream for printers. If None, uses default print().
        """
        if self.is_listening:
            return  # Already listening

        # Setup audio processing pipeline
        file_printer = TapeFilePrinter(stream=output_stream)
        block_printer = BlockPrinter(stream=output_stream)

        listeners: list[TapeFileListener] = [file_printer]
        if file_handler:
            listeners.append(file_handler)

        file_loader = TapeFileLoader(listeners)
        block_parser = BlockParser([block_printer, file_loader])
        byte_decoder = ByteDecoder([block_parser])
        demodulator = AudioDemodulator([byte_decoder], rate=44100)

        # Create and start audio input
        self.audio_in = AudioInput([demodulator], daemon=True, device=self.device)
        self.audio_in.start()
        self.is_listening = True

    def start_recording(
        self, file_handler: TapeFileListener, output_stream: OutputStream | None = None
    ) -> None:
        """Start recording audio input to repository.

        Args:
            file_handler: Handler for received tape files
            output_stream: Optional output stream for printers. If None, uses default print().
        """
        if not self.is_listening:
            self.start_listening(file_handler, output_stream)
        self.is_recording = True

    def stop_audio(self) -> None:
        """Stop all audio operations."""
        if self.audio_in:
            self.audio_in.stop()
            self.audio_in = None
        self.is_listening = False
        self.is_recording = False

    def get_status(self) -> dict[str, Any]:
        """Get current audio status."""
        return {
            "listening": self.is_listening,
            "recording": self.is_recording,
            "device": self.device,
            "active": self.audio_in is not None and self.is_listening,
        }
