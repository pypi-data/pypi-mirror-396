"""Block indicator widget for displaying block status."""

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class StatusLED(QWidget):
    """Simple LED-style status indicator widget."""

    def __init__(self, size: int = 20, parent=None):
        """Initialize status LED.

        Args:
            size: LED diameter in pixels
            parent: Parent widget
        """
        super().__init__(parent)
        self._size = size
        self.color = QColor(128, 128, 128)  # Default gray
        self.setFixedSize(size, size)

    def set_color(self, color: QColor):
        """Set LED color.

        Args:
            color: LED color
        """
        self.color = color
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Paint the LED circle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw outer circle (border)
        pen = QPen(self.color.darker(150))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(self.color)

        # Draw circle
        margin = 2
        painter.drawEllipse(margin, margin, self._size - 2 * margin, self._size - 2 * margin)


class BlockIndicatorWidget(QFrame):
    """Widget for displaying block type and status information.

    Shows:
    - Block type (0x00=Data, 0x01=Header, 0xFF=EOF)
    - Content length
    - Checksum status
    - Block counter
    - Visual LED status indicator
    """

    # Block type constants (from supertape)
    BLOCK_TYPE_DATA = 0x00
    BLOCK_TYPE_HEADER = 0x01
    BLOCK_TYPE_EOF = 0xFF

    def __init__(self, parent=None):
        """Initialize block indicator widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.block_count = 0

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Create the widget layout."""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)

        layout = QVBoxLayout(self)

        # Status LED
        self.led = StatusLED(size=16)
        led_layout = QVBoxLayout()
        led_layout.addWidget(self.led, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(led_layout)

        # Block type label
        self.type_label = QLabel("---")
        self.type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.type_label.font()
        font.setBold(True)
        font.setPointSize(12)
        self.type_label.setFont(font)
        layout.addWidget(self.type_label)

        # Content info label
        self.content_label = QLabel("No data")
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_label.setWordWrap(True)
        layout.addWidget(self.content_label)

        # Counter label
        self.counter_label = QLabel("Blocks: 0")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.counter_label)

        layout.addStretch()

    @Slot(object)
    def update_block(self, data_block):
        """Update display with new block data.

        Args:
            data_block: DataBlock object from supertape
        """
        if data_block is None:
            return

        # Increment counter
        self.block_count += 1
        self.counter_label.setText(f"Blocks: {self.block_count}")

        # Get block type
        block_type = getattr(data_block, "type", None)
        if block_type is None:
            return

        # Update type label and LED color
        if block_type == self.BLOCK_TYPE_HEADER:
            self.type_label.setText("HEADER")
            self.led.set_color(QColor(80, 200, 120))  # Green
            type_name = "Header"
        elif block_type == self.BLOCK_TYPE_DATA:
            self.type_label.setText("DATA")
            self.led.set_color(QColor(74, 144, 226))  # Blue
            type_name = "Data"
        elif block_type == self.BLOCK_TYPE_EOF:
            self.type_label.setText("EOF")
            self.led.set_color(QColor(255, 165, 0))  # Orange
            type_name = "EOF"
        else:
            self.type_label.setText(f"0x{block_type:02X}")
            self.led.set_color(QColor(158, 158, 158))  # Gray
            type_name = f"Type 0x{block_type:02X}"

        # Update content info
        length = getattr(data_block, "length", 0)
        checksum = getattr(data_block, "checksum", None)

        content_text = f"{type_name}\n"
        content_text += f"Length: {length}\n"

        if checksum is not None:
            content_text += f"Checksum: 0x{checksum:02X}"

        self.content_label.setText(content_text)

    @Slot()
    def clear(self):
        """Clear the block indicator display."""
        self.block_count = 0
        self.type_label.setText("---")
        self.content_label.setText("No data")
        self.counter_label.setText("Blocks: 0")
        self.led.set_color(QColor(128, 128, 128))  # Gray

    def reset_counter(self):
        """Reset the block counter."""
        self.block_count = 0
        self.counter_label.setText("Blocks: 0")
