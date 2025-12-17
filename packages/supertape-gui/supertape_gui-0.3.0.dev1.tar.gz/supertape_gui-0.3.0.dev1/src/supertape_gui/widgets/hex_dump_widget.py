"""Hex dump display widget."""

from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from ..utils.formatters import format_hex_line


class HexDumpWidget(QWidget):
    """Widget for displaying progressive hex dump of decoded bytes.

    Shows traditional hex dump format with offset, hex bytes, and ASCII.
    Format: 0000: 48 45 4C 4C 4F 20 57 4F  HELLO WO
    """

    def __init__(self, bytes_per_line: int = 16, parent=None):
        """Initialize hex dump widget.

        Args:
            bytes_per_line: Number of bytes per line (default 16)
            parent: Parent widget
        """
        super().__init__(parent)

        self.bytes_per_line = bytes_per_line
        self.current_line: list[int] = []
        self.offset = 0

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
        font = QFont("Courier New", 9)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_edit.setFont(font)

        # Disable line wrapping for hex dump
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        layout.addWidget(self.text_edit)

    @Slot(int)
    def append_byte(self, byte_value: int):
        """Append a byte to the hex dump display.

        Args:
            byte_value: Byte value (0-255)
        """
        if not (0 <= byte_value <= 255):
            return

        # Add to current line
        self.current_line.append(byte_value)

        # If line is complete, format and display it
        if len(self.current_line) >= self.bytes_per_line:
            self.flush_line()

    def flush_line(self):
        """Format and display the current line if it has any bytes."""
        if not self.current_line:
            return

        # Format the line
        line = format_hex_line(self.offset, self.current_line, self.bytes_per_line)

        # Append to display
        self.text_edit.append(line)

        # Update offset and reset line
        self.offset += len(self.current_line)
        self.current_line = []

        # Auto-scroll to bottom
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @Slot()
    def clear(self):
        """Clear the hex dump display."""
        self.current_line = []
        self.offset = 0
        self.text_edit.clear()

    def get_bytes(self) -> list[int]:
        """Get all bytes including unflushed current line.

        Returns:
            List of all byte values
        """
        # Note: This would require storing all bytes, not implemented
        # for memory efficiency. Could add if needed.
        return list(self.current_line)
