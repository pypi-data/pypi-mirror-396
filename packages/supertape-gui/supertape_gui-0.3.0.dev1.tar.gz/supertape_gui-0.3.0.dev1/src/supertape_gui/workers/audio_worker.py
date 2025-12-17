"""Audio input worker for managing audio recording and listening."""

from PySide6.QtCore import QObject, Signal, Slot


class AudioInputWorker(QObject):
    """Worker for managing audio input pipeline in background thread.

    Handles creation of listener chain and manages AudioInput thread lifecycle.
    """

    # Signals
    finished = Signal()
    error = Signal(str)
    started = Signal()

    def __init__(self, device, pipeline_state):
        """Initialize audio input worker.

        Args:
            device: Audio device index or None for default
            pipeline_state: PipelineState instance for signal coordination
        """
        super().__init__()
        self.device = device
        self.pipeline_state = pipeline_state
        self.audio_input = None

    @Slot()
    def start_listening(self):
        """Start audio input with GUI listeners.

        Creates the listener chain and starts the audio input thread.
        """
        try:
            # Import supertape components
            from supertape.cli.listen import (
                AudioDemodulator,
                AudioInput,
                BlockParser,
                ByteDecoder,
                TapeFileLoader,
            )

            from .gui_listeners import (
                GuiAudioListener,
                GuiBitListener,
                GuiBlockListener,
                GuiByteListener,
                GuiTapeFileListener,
            )

            # Create GUI listeners
            audio_listener = GuiAudioListener(self.pipeline_state)
            bit_listener = GuiBitListener(self.pipeline_state)
            byte_listener = GuiByteListener(self.pipeline_state)
            block_listener = GuiBlockListener(self.pipeline_state)
            file_listener = GuiTapeFileListener(self.pipeline_state)

            # Build listener chain (from bottom up)
            # TapeFileLoader receives blocks and emits complete files
            file_loader = TapeFileLoader([file_listener])

            # BlockParser receives bytes and emits blocks
            block_parser = BlockParser([block_listener, file_loader])

            # ByteDecoder receives bits and emits bytes
            byte_decoder = ByteDecoder([byte_listener, block_parser])

            # AudioDemodulator receives audio and emits bits
            demodulator = AudioDemodulator([bit_listener, byte_decoder], rate=44100)

            # AudioInput captures audio and sends to demodulator
            self.audio_input = AudioInput([audio_listener, demodulator], device=self.device)

            # Mark as listening
            self.pipeline_state.start_listening()

            # Start the audio input thread
            self.audio_input.start()

            self.started.emit()

        except ImportError as e:
            error_msg = f"Failed to import supertape: {e}"
            self.error.emit(error_msg)
            self.pipeline_state.emit_error(error_msg)
            self.finished.emit()

        except Exception as e:
            error_msg = f"Failed to start audio input: {e}"
            self.error.emit(error_msg)
            self.pipeline_state.emit_error(error_msg)
            self.finished.emit()

    @Slot()
    def stop(self):
        """Stop the audio input gracefully."""
        if self.audio_input is not None:
            try:
                self.audio_input.stop()
                self.audio_input.join(timeout=2.0)  # Wait up to 2 seconds
                self.pipeline_state.stop_listening()

            except Exception as e:
                error_msg = f"Error stopping audio input: {e}"
                self.error.emit(error_msg)
                self.pipeline_state.emit_error(error_msg)

            finally:
                self.audio_input = None
                self.finished.emit()
        else:
            self.finished.emit()
