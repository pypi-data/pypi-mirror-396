"""Tape icon widget for displaying tape file metadata."""

import os

from PySide6.QtCore import QMimeData, QPoint, Qt, QUrl, Signal
from PySide6.QtGui import QColor, QDrag, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QMenu, QStyle, QVBoxLayout
from supertape.core.file.api import (
    FILE_TYPE_ASMSRC,
    FILE_TYPE_BASIC,
    FILE_TYPE_DATA,
    FILE_TYPE_MACHINE,
)
from supertape.core.file.save import file_save


class TapeIconWidget(QFrame):
    """Widget for displaying a tape file as an icon with metadata.

    Shows:
    - Icon specific to file type
    - File name
    - File type badge
    - Version/block count metadata

    No click selection - only double-click and context menu interactions.
    """

    # Action signals
    double_clicked = Signal(object)  # TapeFile
    play_requested = Signal(object)  # TapeFile
    edit_requested = Signal(object)  # TapeFile
    delete_requested = Signal(object)  # TapeFile
    info_requested = Signal(object)  # TapeFile
    history_requested = Signal(object)  # TapeFile

    # File type names
    TYPE_NAMES = {
        FILE_TYPE_BASIC: "BASIC",
        FILE_TYPE_DATA: "DATA",
        FILE_TYPE_MACHINE: "MACHINE",
        FILE_TYPE_ASMSRC: "ASM",
    }

    def __init__(self, parent=None):
        """Initialize tape icon widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.tape_file = None
        self.drag_start_position = QPoint()  # Track mouse press for drag threshold
        self.temp_export_dir: str | None = None  # Set by parent MainWindow

        # Setup UI
        self.setup_ui()

        # No frame by default
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Make widget clickable for double-click and context menu
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def setup_ui(self):
        """Create the widget layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)  # Standard margins, no manipulation
        layout.setSpacing(2)  # Tight spacing between elements

        # Icon label (64x64)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setScaledContents(True)
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Filename label
        self.filename_label = QLabel("No file")
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.filename_label.setWordWrap(True)
        font = self.filename_label.font()
        font.setBold(True)
        self.filename_label.setFont(font)
        layout.addWidget(self.filename_label)

        # Type badge label
        self.type_label = QLabel("---")
        self.type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.type_label)

        # Metadata label (blocks, version, etc.)
        self.metadata_label = QLabel("")
        self.metadata_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metadata_label.setWordWrap(True)
        font_small = self.metadata_label.font()
        font_small.setPointSize(8)
        self.metadata_label.setFont(font_small)
        layout.addWidget(self.metadata_label)

        # Set fixed width for consistent grid layout
        self.setFixedWidth(80)  # Narrower (was 120)
        self.setMinimumHeight(100)  # Shorter (was 160)

    def set_tape_file(self, tape_file):
        """Set the tape file to display.

        Args:
            tape_file: TapeFile object from supertape
        """
        self.tape_file = tape_file

        if tape_file is None:
            self.clear()
            return

        # Get file name
        name = getattr(tape_file, "fname", "Unknown")
        self.filename_label.setText(name)

        # Get file type
        ftype = getattr(tape_file, "ftype", None)
        type_name = self.TYPE_NAMES.get(ftype, f"0x{ftype:02X}" if ftype is not None else "---")
        self.type_label.setText(type_name)

        # Set icon based on type
        self.set_icon_for_type(ftype)

        # Get metadata - file size in bytes
        fbody = getattr(tape_file, "fbody", [])
        body_size = len(fbody) if fbody else 0

        metadata_text = f"{body_size} bytes"
        self.metadata_label.setText(metadata_text)

    def set_icon_for_type(self, ftype):
        """Set the icon based on file type.

        Args:
            ftype: File type constant
        """
        # Map file types to icon file names
        icon_map = {
            FILE_TYPE_BASIC: "tape_basic.svg",
            FILE_TYPE_DATA: "tape_data.svg",
            FILE_TYPE_MACHINE: "tape_machine.svg",
            FILE_TYPE_ASMSRC: "tape_asm.svg",
        }

        icon_filename = icon_map.get(ftype, "tape_data.svg")

        # Try to load icon from resources
        resources_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "resources", "icons"
        )
        icon_path = os.path.join(resources_dir, icon_filename)

        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.icon_label.setPixmap(pixmap)
        else:
            # Fallback to colored text if icon not found
            color_map = {
                FILE_TYPE_BASIC: "#C0392B",  # Classic red
                FILE_TYPE_DATA: "#6E2C1F",  # Burgundy
                FILE_TYPE_MACHINE: "#884440",  # Charcoal red
                FILE_TYPE_ASMSRC: "#D35A4E",  # Coral
            }
            color = color_map.get(ftype, "#000000")
            type_name = self.TYPE_NAMES.get(ftype, "?")
            self.icon_label.setText(
                f'<span style="color: {color}; font-size: 24pt;">{type_name}</span>'
            )

    def set_temp_export_dir(self, temp_dir: str):
        """Set temporary directory for drag export operations.

        Args:
            temp_dir: Path to temporary directory (managed by MainWindow)
        """
        self.temp_export_dir = temp_dir

    def clear(self):
        """Clear the tape display."""
        self.tape_file = None
        self.filename_label.setText("No file")
        self.type_label.setText("---")
        self.metadata_label.setText("")
        self.icon_label.clear()

    def mousePressEvent(self, event):
        """Store position for drag threshold detection.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton and self.tape_file is not None:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Initiate drag if mouse moved beyond threshold.

        Args:
            event: Mouse event
        """
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if self.tape_file is None or self.temp_export_dir is None:
            return

        # Check drag threshold
        if (
            event.pos() - self.drag_start_position
        ).manhattanLength() < QApplication.startDragDistance():
            return

        self.start_drag()

    def start_drag(self):
        """Execute drag operation with tape file export."""
        try:
            # Create temporary .k7 file
            filename = f"{self.tape_file.fname}.k7"
            temp_file_path = os.path.join(self.temp_export_dir, filename)

            # Export tape to temp file
            file_save(temp_file_path, self.tape_file)

            # Create MIME data with file URL
            mime_data = QMimeData()
            url = QUrl.fromLocalFile(temp_file_path)
            mime_data.setUrls([url])

            # Create drag with icon pixmap
            drag = QDrag(self)
            drag.setMimeData(mime_data)

            if not self.icon_label.pixmap().isNull():
                pixmap = self.icon_label.pixmap()
                drag.setPixmap(pixmap)
                drag.setHotSpot(pixmap.rect().center())

            # Execute drag (blocking until drop/cancel)
            drag.exec(Qt.DropAction.CopyAction)

        except Exception as e:
            # Silent failure to not disrupt drag gesture
            print(f"Drag export failed: {e}")

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to play tape.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton and self.tape_file is not None:
            self.double_clicked.emit(self.tape_file)
            self.play_requested.emit(self.tape_file)
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        """Show context menu on right-click.

        Args:
            event: Context menu event
        """
        if self.tape_file is None:
            return

        menu = QMenu(self)

        # Force light background for readability on selected icons
        palette = menu.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(227, 242, 253))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        menu.setPalette(palette)

        # Play action
        play_action = menu.addAction("Play")
        play_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        play_action.triggered.connect(lambda: self.play_requested.emit(self.tape_file))

        menu.addSeparator()

        # Edit action
        edit_action = menu.addAction("Edit")
        edit_action.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        )
        edit_action.triggered.connect(lambda: self.edit_requested.emit(self.tape_file))

        # Get Information action
        info_action = menu.addAction("Get Information...")
        info_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView))
        info_action.triggered.connect(lambda: self.info_requested.emit(self.tape_file))

        # Show History action
        history_action = menu.addAction("Show History...")
        history_action.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogListView)
        )
        history_action.triggered.connect(lambda: self.history_requested.emit(self.tape_file))

        menu.addSeparator()

        # Delete action
        delete_action = menu.addAction("Delete...")
        delete_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self.tape_file))

        menu.exec(event.globalPos())
