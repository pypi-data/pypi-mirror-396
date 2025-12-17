"""GUI listeners for bridging supertape callbacks to Qt signals."""

from PySide6.QtCore import QObject
from supertape.core.audio.api import AudioSignalListener, BitListener
from supertape.core.file.api import BlockListener, ByteListener, TapeFileListener


# Combined metaclasses to resolve metaclass conflicts between Qt and supertape classes
class AudioListenerMeta(type(QObject), type(AudioSignalListener)):  # type: ignore[misc]
    """Metaclass combining QObject and AudioSignalListener metaclasses."""

    pass


class BitListenerMeta(type(QObject), type(BitListener)):  # type: ignore[misc]
    """Metaclass combining QObject and BitListener metaclasses."""

    pass


class ByteListenerMeta(type(QObject), type(ByteListener)):  # type: ignore[misc]
    """Metaclass combining QObject and ByteListener metaclasses."""

    pass


class BlockListenerMeta(type(QObject), type(BlockListener)):  # type: ignore[misc]
    """Metaclass combining QObject and BlockListener metaclasses."""

    pass


class TapeFileListenerMeta(type(QObject), type(TapeFileListener)):  # type: ignore[misc]
    """Metaclass combining QObject and TapeFileListener metaclasses."""

    pass


class GuiAudioListener(AudioSignalListener, QObject, metaclass=AudioListenerMeta):
    """Listener for audio samples from the audio input stream.

    Forwards audio samples to PipelineState via Qt signals for
    thread-safe GUI updates.
    """

    def __init__(self, pipeline_state):
        """Initialize GUI audio listener.

        Args:
            pipeline_state: PipelineState instance to emit signals to
        """
        super().__init__()
        self.pipeline_state = pipeline_state

    def process_samples(self, data):
        """Process audio samples from the audio input.

        This method is called by the audio input stream.

        Args:
            data: Sequence of audio samples (int16 values)
        """
        # Emit to pipeline state (thread-safe via Qt queued connections)
        self.pipeline_state.input_audio_data.emit(data)


class GuiBitListener(BitListener, QObject, metaclass=BitListenerMeta):
    """Listener for bits decoded from audio.

    Forwards bit characters to PipelineState via Qt signals.
    """

    def __init__(self, pipeline_state):
        """Initialize GUI bit listener.

        Args:
            pipeline_state: PipelineState instance to emit signals to
        """
        super().__init__()
        self.pipeline_state = pipeline_state

    def process_bit(self, value):
        """Process a decoded bit.

        This method is called by the audio demodulator.

        Args:
            value: Bit value (0 or 1)
        """
        # Convert to character representation
        if value == 0:
            bit_char = "0"
        elif value == 1:
            bit_char = "1"
        else:
            bit_char = "-"  # Invalid or sync

        # Emit to pipeline state
        self.pipeline_state.input_bit_data.emit(bit_char)

    def process_silence(self):
        """Process silence detection.

        This method is called by the audio demodulator during silence.
        """
        # Emit silence as '-' character
        self.pipeline_state.input_bit_data.emit("-")


class GuiByteListener(ByteListener, QObject, metaclass=ByteListenerMeta):
    """Listener for bytes decoded from bit stream.

    Forwards byte values to PipelineState via Qt signals.
    """

    def __init__(self, pipeline_state):
        """Initialize GUI byte listener.

        Args:
            pipeline_state: PipelineState instance to emit signals to
        """
        super().__init__()
        self.pipeline_state = pipeline_state

    def process_byte(self, value):
        """Process a decoded byte.

        This method is called by the byte decoder.

        Args:
            value: Byte value (0-255)
        """
        # Emit to pipeline state
        self.pipeline_state.input_byte_data.emit(value)

    def process_silence(self):
        """Process silence detection.

        This method is called by the byte decoder during silence.
        We don't need to visualize byte-level silence, so this is a no-op.
        """
        pass


class GuiBlockListener(BlockListener, QObject, metaclass=BlockListenerMeta):
    """Listener for data blocks parsed from byte stream.

    Forwards DataBlock objects to PipelineState via Qt signals.
    """

    def __init__(self, pipeline_state):
        """Initialize GUI block listener.

        Args:
            pipeline_state: PipelineState instance to emit signals to
        """
        super().__init__()
        self.pipeline_state = pipeline_state

    def process_block(self, block):
        """Process a parsed data block.

        This method is called by the block parser.

        Args:
            block: DataBlock object from supertape
        """
        # Emit to pipeline state
        self.pipeline_state.input_block_data.emit(block)


class GuiTapeFileListener(TapeFileListener, QObject, metaclass=TapeFileListenerMeta):
    """Listener for complete tape files assembled from blocks.

    Forwards TapeFile objects to PipelineState via Qt signals.
    """

    def __init__(self, pipeline_state):
        """Initialize GUI tape file listener.

        Args:
            pipeline_state: PipelineState instance to emit signals to
        """
        super().__init__()
        self.pipeline_state = pipeline_state

    def process_file(self, file):
        """Process a complete tape file.

        This method is called by the tape file loader.

        Args:
            file: TapeFile object from supertape
        """
        # Emit to pipeline state
        self.pipeline_state.tape_received.emit(file)


class GuiAudioPlayerObserver(QObject):
    """Observer for audio playback operations.

    Forwards playback data and progress to PipelineState via Qt signals.
    This implements the observer pattern used by supertape's play_file().
    """

    def __init__(self, pipeline_state):
        """Initialize GUI audio player observer.

        Args:
            pipeline_state: PipelineState instance to emit signals to
        """
        super().__init__()
        self.pipeline_state = pipeline_state

    def on_start(self):
        """Called when playback starts."""
        self.pipeline_state.start_playing()

    def on_block(self, data_block):
        """Called when a block is being played.

        Args:
            data_block: DataBlock being played
        """
        self.pipeline_state.output_block_data.emit(data_block)

    def on_byte(self, byte_value):
        """Called when a byte is being played.

        Args:
            byte_value: Byte value (0-255)
        """
        self.pipeline_state.output_byte_data.emit(byte_value)

    def on_bit(self, bit_value):
        """Called when a bit is being played.

        Args:
            bit_value: Bit value (0 or 1)
        """
        # Convert to character representation
        bit_char = "1" if bit_value else "0"
        self.pipeline_state.output_bit_data.emit(bit_char)

    def on_audio_samples(self, samples):
        """Called when audio samples are generated.

        Args:
            samples: Audio samples being played
        """
        self.pipeline_state.output_audio_data.emit(samples)

    def on_progress(self, percent):
        """Called to report playback progress.

        Args:
            percent: Progress percentage (0-100)
        """
        self.pipeline_state.progress_updated.emit(percent)

    def on_complete(self):
        """Called when playback completes."""
        self.pipeline_state.stop_playing()

    def on_error(self, error_message):
        """Called when an error occurs during playback.

        Args:
            error_message: Error message string
        """
        self.pipeline_state.emit_error(error_message)
