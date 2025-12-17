"""Bit stream visualization widget."""

from collections import deque

from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from ..utils.formatters import format_bit_stream


class BitsViewWidget(QWidget):
    """Widget for displaying stream of bits as they are decoded.

    Shows '0', '1', and '-' (invalid/sync) with color coding.
    Auto-scrolls to show most recent bits.
    """

    def __init__(self, max_bits: int = 1000, parent=None):
        """Initialize bits view widget.

        Args:
            max_bits: Maximum number of bits to display (default 1000)
            parent: Parent widget
        """
        super().__init__(parent)

        self.max_bits = max_bits
        self.bit_buffer: deque[str] = deque(maxlen=max_bits)

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Create the text display widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create text edit widget
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        # Set monospace font
        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_edit.setFont(font)

        # Enable line wrapping
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

        layout.addWidget(self.text_edit)

    @Slot(str)
    def append_bit(self, bit_char: str):
        """Append a bit character to the display.

        Args:
            bit_char: '0', '1', or '-' (invalid/sync)
        """
        if bit_char not in ("0", "1", "-"):
            return

        # Add to buffer
        self.bit_buffer.append(bit_char)

        # Format with color
        html, _ = format_bit_stream(bit_char)

        # Append to display
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.insertHtml(html)

        # Auto-scroll to bottom
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @Slot()
    def clear(self):
        """Clear the bit stream display."""
        self.bit_buffer.clear()
        self.text_edit.clear()

    def get_bits(self) -> str:
        """Get all bits as a string.

        Returns:
            String of all bits
        """
        return "".join(self.bit_buffer)
