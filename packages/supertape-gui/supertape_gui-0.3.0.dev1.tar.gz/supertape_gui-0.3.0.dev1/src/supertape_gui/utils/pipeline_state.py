"""Central state manager for audio pipeline."""

from PySide6.QtCore import QObject, Signal


class PipelineState(QObject):
    """Central state manager for audio pipeline status and data flow.

    Coordinates all data flow between audio threads and GUI widgets through
    Qt signals. Provides thread-safe communication via queued connections.
    """

    # State signals
    recording_started = Signal()
    recording_stopped = Signal()
    playing_started = Signal()
    playing_stopped = Signal()
    listening_started = Signal()
    listening_stopped = Signal()
    error_occurred = Signal(str)  # Error message

    # Input pipeline data signals (recording/listening)
    input_audio_data = Signal(object)  # Audio samples (list or numpy array)
    input_bit_data = Signal(str)  # Bit character: '0', '1', '-'
    input_byte_data = Signal(int)  # Byte value (0-255)
    input_block_data = Signal(object)  # DataBlock object
    tape_received = Signal(object)  # TapeFile object

    # Output pipeline data signals (playing)
    output_block_data = Signal(object)  # DataBlock object
    output_byte_data = Signal(int)  # Byte value (0-255)
    output_bit_data = Signal(str)  # Bit character: '0', '1'
    output_audio_data = Signal(object)  # Audio samples

    # Progress signals
    progress_updated = Signal(int)  # Progress percentage (0-100)

    def __init__(self):
        """Initialize pipeline state."""
        super().__init__()

        # State flags
        self.is_recording = False
        self.is_playing = False
        self.is_listening = False

    def start_recording(self):
        """Mark recording as started."""
        self.is_recording = True
        self.recording_started.emit()

    def stop_recording(self):
        """Mark recording as stopped."""
        self.is_recording = False
        self.recording_stopped.emit()

    def start_playing(self):
        """Mark playing as started."""
        self.is_playing = True
        self.playing_started.emit()

    def stop_playing(self):
        """Mark playing as stopped."""
        self.is_playing = False
        self.playing_stopped.emit()

    def start_listening(self):
        """Mark listening as started."""
        self.is_listening = True
        self.listening_started.emit()

    def stop_listening(self):
        """Mark listening as stopped."""
        self.is_listening = False
        self.listening_stopped.emit()

    def emit_error(self, message: str):
        """Emit an error message.

        Args:
            message: Error message text
        """
        self.error_occurred.emit(message)

    def reset(self):
        """Reset all state flags."""
        self.is_recording = False
        self.is_playing = False
        self.is_listening = False
