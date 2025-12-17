"""DAW-style waveform visualization widget using QPainter."""

from PySide6.QtCore import QPointF, Qt, QTimer, Slot
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

from ..utils.audio_buffer import AudioRingBuffer


class WaveformWidget(QWidget):
    """Real-time audio waveform visualization widget.

    Displays scrolling waveform in DAW style (mirrored from center,
    right-to-left scrolling). Uses custom QPainter rendering for
    lightweight, high-performance visualization.
    """

    def __init__(self, sample_rate: int = 44100, display_seconds: float = 2.0, parent=None):
        """Initialize waveform widget.

        Args:
            sample_rate: Audio sample rate in Hz (default 44100)
            display_seconds: Number of seconds to display (default 2.0)
            parent: Parent widget
        """
        super().__init__(parent)

        # Configuration
        self.sample_rate = sample_rate
        self.display_seconds = display_seconds

        # Data storage - ring buffer
        buffer_size = int(sample_rate * display_seconds)
        self.audio_buffer = AudioRingBuffer(maxlen=buffer_size)

        # Visual settings
        self.background_color = QColor(30, 30, 30)  # Dark gray
        self.waveform_color = QColor(80, 200, 120, 180)  # Semi-transparent green
        self.center_line_color = QColor(60, 60, 60)  # Subtle gray

        # Paint throttling - limit redraws to ~30 FPS
        self.needs_redraw = False
        self.paint_timer = QTimer()
        self.paint_timer.timeout.connect(self._scheduled_repaint)
        self.paint_timer.start(33)  # ~30 FPS (33ms interval)

        # Set minimum size
        self.setMinimumSize(200, 60)

    @Slot(object)
    def update_data(self, samples):
        """Update waveform with new audio samples.

        Args:
            samples: List or numpy array of audio sample values (int16)
        """
        if not samples:
            return

        # Add samples to ring buffer
        if hasattr(samples, "__iter__"):
            self.audio_buffer.append(list(samples))
        else:
            self.audio_buffer.append([samples])

        # Mark for redrawing (actual repaint handled by timer)
        self.needs_redraw = True

    @Slot()
    def clear(self):
        """Clear the waveform display."""
        self.audio_buffer.clear()
        self.needs_redraw = True

    def _scheduled_repaint(self):
        """Timer callback for throttled repainting."""
        if self.needs_redraw:
            self.needs_redraw = False
            self.update()  # Schedule paintEvent

    def paintEvent(self, event):
        """Render the waveform using QPainter."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fill background
        painter.fillRect(self.rect(), self.background_color)

        # Get dimensions
        width = self.width()
        height = self.height()
        center_y = height / 2.0

        # Draw center line
        painter.setPen(QPen(self.center_line_color, 1))
        painter.drawLine(0, int(center_y), width, int(center_y))

        # Get buffer data
        samples = self.audio_buffer.get_data()
        if not samples:
            return

        # Downsample to widget width
        downsampled = self._downsample_for_display(samples, width)
        if not downsampled:
            return

        # Build polygon from downsampled data
        polygon = QPolygonF()

        # Add top edge (positive peaks)
        for i, (min_val, max_val) in enumerate(downsampled):
            x = i
            # Normalize int16 to 0.0-1.0 range, then center at 0.5
            normalized_max = (max_val + 32768.0) / 65535.0
            # Map to pixel Y (inverted: 0 is top)
            y = center_y - ((normalized_max - 0.5) * height)
            polygon.append(QPointF(x, y))

        # Add bottom edge (negative peaks) in reverse
        for i in range(len(downsampled) - 1, -1, -1):
            min_val, max_val = downsampled[i]
            x = i
            normalized_min = (min_val + 32768.0) / 65535.0
            y = center_y - ((normalized_min - 0.5) * height)
            polygon.append(QPointF(x, y))

        # Draw filled polygon
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.waveform_color)
        painter.drawPolygon(polygon)

    def _downsample_for_display(self, samples, target_width):
        """Downsample audio data to fit display width using min-max.

        Args:
            samples: List of int16 samples
            target_width: Widget width in pixels

        Returns:
            List of (min, max) tuples, one per pixel column
        """
        if not samples:
            return []

        num_samples = len(samples)

        # If fewer samples than pixels, no downsampling needed
        if num_samples <= target_width:
            return [(s, s) for s in samples]

        # Calculate samples per pixel
        samples_per_pixel = num_samples / target_width

        downsampled = []
        for pixel_x in range(target_width):
            # Calculate sample range for this pixel
            start_idx = int(pixel_x * samples_per_pixel)
            end_idx = int((pixel_x + 1) * samples_per_pixel)

            # Get slice of samples for this pixel
            pixel_samples = samples[start_idx:end_idx]

            if pixel_samples:
                min_val = min(pixel_samples)
                max_val = max(pixel_samples)
                downsampled.append((min_val, max_val))
            else:
                downsampled.append((0, 0))

        return downsampled
