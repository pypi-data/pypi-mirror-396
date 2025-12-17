"""Dialog for displaying git history of a tape file."""

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
from supertape.core.file.api import TapeFile
from supertape.core.repository.dulwich_repo import DulwichRepository


class TapeHistoryDialog(QDialog):
    """Dialog for displaying git commit history for a tape file."""

    def __init__(self, tape_file: TapeFile, repository: DulwichRepository, parent=None):
        """Initialize tape history dialog.

        Args:
            tape_file: TapeFile object to show history for
            repository: Repository to query for history
            parent: Parent widget
        """
        super().__init__(parent)
        self.tape_file = tape_file
        self.repository = repository
        self.versions: list = []

        self.setWindowTitle(f"History: {tape_file.fname}")
        self.setMinimumSize(800, 400)

        # Setup UI
        self.setup_ui()

        # Load history
        self.load_history()

    def setup_ui(self):
        """Create dialog UI."""
        layout = QVBoxLayout(self)

        # Info label
        self.info_label = QLabel("Loading history...")
        layout.addWidget(self.info_label)

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Commit Hash", "Date/Time", "Message", "Author", "Status"]
        )

        # Configure table
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)

        # Stretch columns
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Double-click to copy commit hash
        self.table.doubleClicked.connect(self.copy_commit_hash)

        layout.addWidget(self.table)

        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)

    def load_history(self):
        """Load git history from repository."""
        try:
            self.versions = self.repository.get_tape_file_versions(self.tape_file.fname)

            if not self.versions:
                self.info_label.setText("No history available for this file.")
                self.table.setVisible(False)
                return

            # Update info label
            self.info_label.setText(
                f"Showing {len(self.versions)} commit(s) for {self.tape_file.fname}"
            )

            # Populate table
            self.table.setRowCount(len(self.versions))

            # Find current version (newest non-deleted)
            current_hash = None
            for version in self.versions:
                if not version.is_deleted:
                    current_hash = version.commit_hash
                    break

            for row, version in enumerate(self.versions):
                # Commit hash (short form - 8 chars)
                hash_item = QTableWidgetItem(version.commit_hash[:8])
                hash_item.setData(Qt.ItemDataRole.UserRole, version.commit_hash)  # Store full hash
                self.table.setItem(row, 0, hash_item)

                # Date/Time
                dt = datetime.fromtimestamp(version.timestamp)
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                date_item = QTableWidgetItem(date_str)
                self.table.setItem(row, 1, date_item)

                # Message
                msg_item = QTableWidgetItem(version.commit_message)
                self.table.setItem(row, 2, msg_item)

                # Author
                author_item = QTableWidgetItem(version.author)
                self.table.setItem(row, 3, author_item)

                # Status
                if version.is_deleted:
                    status = "Deleted"
                    status_item = QTableWidgetItem(status)
                    # Red text for deleted commits
                    status_item.setForeground(QBrush(QColor(255, 0, 0)))
                    # Make all cells in row red
                    for col in range(5):
                        self.table.item(row, col).setForeground(QBrush(QColor(255, 0, 0)))
                elif version.commit_hash == current_hash:
                    status = "Current"
                    status_item = QTableWidgetItem(status)
                    # Bold font for current version
                    font = QFont()
                    font.setBold(True)
                    for col in range(5):
                        self.table.item(row, col).setFont(font)
                else:
                    status = ""
                    status_item = QTableWidgetItem(status)

                self.table.setItem(row, 4, status_item)

        except Exception as e:
            self.info_label.setText(f"Error loading history: {e}")
            self.table.setVisible(False)
            QMessageBox.critical(self, "History Error", f"Failed to load git history:\n{e}")

    def copy_commit_hash(self):
        """Copy commit hash from double-clicked row to clipboard."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            hash_item = self.table.item(current_row, 0)
            if hash_item:
                full_hash = hash_item.data(Qt.ItemDataRole.UserRole)
                clipboard = QGuiApplication.clipboard()
                clipboard.setText(full_hash)

                # Show brief feedback
                self.info_label.setText(
                    f"Copied commit hash: {full_hash[:8]} (full hash in clipboard)"
                )

    @staticmethod
    def show_history(tape_file: TapeFile, repository: DulwichRepository, parent=None):
        """Show tape history dialog.

        Args:
            tape_file: TapeFile object to show history for
            repository: Repository to query for history
            parent: Parent widget
        """
        dialog = TapeHistoryDialog(tape_file, repository, parent)
        dialog.exec()
