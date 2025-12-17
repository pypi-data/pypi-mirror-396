"""Tape collection widget for displaying multiple tape files."""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PySide6.QtWidgets import QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from ..utils import FileCompiler
from .tape_icon_widget import TapeIconWidget


class TapeCollectionWidget(QScrollArea):
    """Widget for displaying a collection of tape files.

    Shows tape files in a grid layout with scroll support.
    No selection state - interactions via double-click and context menu only.
    """

    # Signal emitted when files are dropped
    file_dropped = Signal(list)  # List of file paths

    # Action forwarding signals
    tape_double_clicked = Signal(object)
    tape_play_requested = Signal(object)
    tape_edit_requested = Signal(object)
    tape_delete_requested = Signal(object)
    tape_info_requested = Signal(object)
    tape_history_requested = Signal(object)

    def __init__(self, columns: int = 4, parent=None):
        """Initialize tape collection widget.

        Args:
            columns: Number of columns in the grid (minimum, will auto-adjust to width)
            parent: Parent widget
        """
        super().__init__(parent)

        self.min_columns = 4  # Minimum columns to show
        self.columns = columns
        self.tape_widgets: list[TapeIconWidget] = []
        self.tape_data: list[tuple] = []  # Store (tape_file, timestamp) tuples
        self.temp_export_dir: str | None = None  # Set by MainWindow
        self.repository = None  # Set by MainWindow for timestamp lookups
        self.icon_width = 80  # Fixed icon width
        self.icon_spacing = 10  # Grid spacing

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Create scroll area with icon grid."""
        # Create container widget
        self.container = QWidget()
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Grid layout for tape icons - compact with fixed spacing
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.grid_layout)
        layout.addStretch()

        # Empty state label
        self.empty_label = QLabel("No tapes loaded")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.empty_label.font()
        font.setPointSize(12)
        font.setItalic(True)
        self.empty_label.setFont(font)
        self.empty_label.setStyleSheet("color: #9E9E9E;")
        layout.addWidget(self.empty_label)

        # Set container as scroll area widget
        self.setWidget(self.container)
        self.setWidgetResizable(True)

        # Configure scroll area
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def set_temp_export_dir(self, temp_dir: str):
        """Set temporary directory for drag export operations.

        Args:
            temp_dir: Path to temporary directory
        """
        self.temp_export_dir = temp_dir

        # Update existing widgets
        for tape_widget in self.tape_widgets:
            tape_widget.set_temp_export_dir(temp_dir)

    def set_repository(self, repository):
        """Set repository for timestamp lookups.

        Args:
            repository: TapeFileRepository instance or None
        """
        self.repository = repository

    def _find_insert_position(self, tape_file) -> int:
        """Find correct insert position for alphabetical order.

        Uses binary search to find insertion point where tape_file
        should be inserted to maintain case-insensitive alphabetical order.

        Args:
            tape_file: TapeFile object to insert

        Returns:
            Index where tape_file should be inserted
        """
        import bisect

        # Extract sort keys from existing tapes (case-insensitive)
        sort_keys = [t[0].fname.upper() for t in self.tape_data]
        new_key = tape_file.fname.upper()

        # Binary search for insertion point
        return bisect.bisect_left(sort_keys, new_key)

    def add_tape(self, tape_file, timestamp: Optional[int] = None):
        """Add a tape file to the collection.

        Args:
            tape_file: TapeFile object from supertape
            timestamp: Optional Unix timestamp from repository
        """
        # Find correct insertion position for alphabetical order
        insert_index = self._find_insert_position(tape_file)

        # Insert into data storage at correct position
        self.tape_data.insert(insert_index, (tape_file, timestamp))

        # Create tape icon widget
        tape_widget = TapeIconWidget()
        tape_widget.set_tape_file(tape_file)

        # Configure temp directory for drag export
        if self.temp_export_dir:
            tape_widget.set_temp_export_dir(self.temp_export_dir)

        # Connect action signals
        tape_widget.double_clicked.connect(self.tape_double_clicked.emit)
        tape_widget.play_requested.connect(self.tape_play_requested.emit)
        tape_widget.edit_requested.connect(self.tape_edit_requested.emit)
        tape_widget.delete_requested.connect(self.tape_delete_requested.emit)
        tape_widget.info_requested.connect(self.tape_info_requested.emit)
        tape_widget.history_requested.connect(self.tape_history_requested.emit)

        # Insert widget at correct position
        self.tape_widgets.insert(insert_index, tape_widget)

        # Rebuild grid to reflect new positions
        self._relayout_widgets()

        # Hide empty label
        self.empty_label.hide()

    def remove_tape(self, index: int):
        """Remove a tape from the collection by index.

        Args:
            index: Index of tape to remove
        """
        if not (0 <= index < len(self.tape_data)):
            return

        # Remove from data storage
        self.tape_data.pop(index)

        # Remove from icon grid
        if 0 <= index < len(self.tape_widgets):
            tape_widget = self.tape_widgets.pop(index)
            self.grid_layout.removeWidget(tape_widget)
            tape_widget.deleteLater()
            self._relayout_widgets()

        # Show empty label if no tapes
        if not self.tape_data:
            self.empty_label.show()

    def clear(self):
        """Clear all tapes from the collection."""
        # Clear data storage
        self.tape_data = []

        # Clear icon view widgets
        for tape_widget in self.tape_widgets:
            self.grid_layout.removeWidget(tape_widget)
            tape_widget.deleteLater()
        self.tape_widgets = []

        # Show empty label
        self.empty_label.show()

    def get_tape_count(self) -> int:
        """Get the number of tapes in the collection.

        Returns:
            Number of tapes
        """
        return len(self.tape_widgets)

    def get_tape_at(self, index: int):
        """Get tape file at specified index.

        Args:
            index: Index of tape

        Returns:
            TapeFile object or None
        """
        if 0 <= index < len(self.tape_widgets):
            return self.tape_widgets[index].tape_file
        return None

    def _calculate_columns(self) -> int:
        """Calculate number of columns based on available width.

        Returns:
            Number of columns that can fit
        """
        available_width = self.viewport().width()
        # Each icon takes icon_width + spacing, minus one spacing at the end
        # Add some margin for scrollbar
        usable_width = available_width - 20
        cols = max(self.min_columns, usable_width // (self.icon_width + self.icon_spacing))
        return int(cols)

    def _relayout_widgets(self):
        """Re-layout all widgets in the grid."""
        for index, tape_widget in enumerate(self.tape_widgets):
            row = index // self.columns
            col = index % self.columns
            self.grid_layout.addWidget(tape_widget, row, col)

    def resizeEvent(self, event):
        """Handle resize to adjust column count dynamically.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)

        # Calculate new column count based on width
        new_columns = self._calculate_columns()

        # Only relayout if column count changed
        if new_columns != self.columns:
            self.columns = new_columns
            self._relayout_widgets()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept file drops and show visual feedback.

        Args:
            event: Drag enter event
        """
        if event.mimeData().hasUrls():
            # Check if at least one file is supported
            for url in event.mimeData().urls():
                if url.isLocalFile() and FileCompiler.is_supported_file(url.toLocalFile()):
                    event.acceptProposedAction()
                    self.setStyleSheet("QScrollArea { border: 2px dashed #4CAF50; }")
                    return
        event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        """Remove visual feedback when drag leaves.

        Args:
            event: Drag leave event
        """
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        """Process dropped files.

        Args:
            event: Drop event
        """
        self.setStyleSheet("")

        # Extract local file paths
        files = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile() and FileCompiler.is_supported_file(url.toLocalFile())
        ]

        if files:
            event.acceptProposedAction()
            self.file_dropped.emit(files)
