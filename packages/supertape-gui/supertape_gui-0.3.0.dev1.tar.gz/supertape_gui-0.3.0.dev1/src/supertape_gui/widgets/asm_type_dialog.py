"""Dialog for selecting assembly file compilation mode."""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QRadioButton,
    QVBoxLayout,
)


class AsmTypeDialog(QDialog):
    """Dialog for selecting how to import an assembly file."""

    def __init__(self, filename: str, parent=None):
        """Initialize assembly type selection dialog.

        Args:
            filename: Name of the assembly file being imported
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Assembly File Import")
        self.selected_mode = None

        # Setup UI
        self.setup_ui(filename)

    def setup_ui(self, filename: str):
        """Create dialog UI.

        Args:
            filename: Name of the assembly file
        """
        layout = QVBoxLayout(self)

        # Question label
        question = QLabel(f"How should <b>{filename}</b> be imported?")
        question.setWordWrap(True)
        layout.addWidget(question)

        # Add spacing
        layout.addSpacing(10)

        # Radio button: MACHINE (default)
        self.machine_radio = QRadioButton("Executable Machine Code (MACHINE)")
        self.machine_radio.setChecked(True)
        layout.addWidget(self.machine_radio)

        # Description for MACHINE
        machine_desc = QLabel("Assemble to binary and store as executable (type 0x02)")
        machine_desc.setStyleSheet("color: #757575; padding-left: 20px;")
        machine_desc.setWordWrap(True)
        layout.addWidget(machine_desc)

        layout.addSpacing(10)

        # Radio button: ASMSRC
        self.asmsrc_radio = QRadioButton("Assembly Source Text (ASMSRC)")
        layout.addWidget(self.asmsrc_radio)

        # Description for ASMSRC
        asmsrc_desc = QLabel("Store as text for later editing (type 0x05)")
        asmsrc_desc.setStyleSheet("color: #757575; padding-left: 20px;")
        asmsrc_desc.setWordWrap(True)
        layout.addWidget(asmsrc_desc)

        # Add stretch
        layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Set dialog size
        self.setMinimumWidth(400)

    def accept(self):
        """Handle OK button click."""
        if self.machine_radio.isChecked():
            self.selected_mode = "machine"
        else:
            self.selected_mode = "asmsrc"
        super().accept()

    def reject(self):
        """Handle Cancel button click."""
        self.selected_mode = None
        super().reject()

    @staticmethod
    def ask_mode(filename: str, parent=None) -> str | None:
        """Show dialog and return selected mode.

        Args:
            filename: Name of the assembly file
            parent: Parent widget

        Returns:
            'machine', 'asmsrc', or None if cancelled
        """
        dialog = AsmTypeDialog(filename, parent)
        dialog.exec()
        return dialog.selected_mode
