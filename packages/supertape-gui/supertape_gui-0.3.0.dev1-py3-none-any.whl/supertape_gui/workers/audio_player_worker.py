"""Audio player worker for managing audio playback."""

from PySide6.QtCore import QObject, Signal, Slot


class AudioPlayerWorker(QObject):
    """Worker for managing audio playback in background thread.

    Handles playback of TapeFile with monitoring via observer pattern.
    """

    # Signals
    finished = Signal()
    error = Signal(str)
    progress = Signal(int)  # Progress percentage
    started = Signal()

    def __init__(self, tape_file, device, pipeline_state):
        """Initialize audio player worker.

        Args:
            tape_file: TapeFile object to play
            device: Audio device index or None for default
            pipeline_state: PipelineState instance for signal coordination
        """
        super().__init__()
        self.tape_file = tape_file
        self.device = device
        self.pipeline_state = pipeline_state

    @Slot()
    def play(self):
        """Play the tape file with GUI monitoring.

        Uses GuiAudioPlayerObserver to forward playback events to PipelineState.
        """
        if self.tape_file is None:
            self.error.emit("No tape file to play")
            self.finished.emit()
            return

        try:
            # Import supertape components
            from supertape.cli.play import play_file

            from .gui_listeners import GuiAudioPlayerObserver

            # Create GUI observer
            observer = GuiAudioPlayerObserver(self.pipeline_state)

            # Connect observer signals to our signals
            self.pipeline_state.progress_updated.connect(self.progress.emit)

            self.started.emit()

            # Play the file (this blocks until complete)
            play_file(file=self.tape_file, observer=observer, device=self.device)

            # Playback complete
            self.finished.emit()

        except ImportError as e:
            error_msg = f"Failed to import supertape: {e}"
            self.error.emit(error_msg)
            self.pipeline_state.emit_error(error_msg)
            self.finished.emit()

        except Exception as e:
            error_msg = f"Failed to play file: {e}"
            self.error.emit(error_msg)
            self.pipeline_state.emit_error(error_msg)
            self.finished.emit()

    @Slot()
    def stop(self):
        """Stop playback.

        Note: The supertape play_file() function doesn't currently support
        stopping mid-playback, so this just marks completion.
        """
        self.pipeline_state.stop_playing()
        self.finished.emit()
