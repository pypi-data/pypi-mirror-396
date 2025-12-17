"""Dialog for configuring external text editor."""

import platform

from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)


class EditorConfigDialog(QDialog):
    """Dialog for configuring external text editor preference."""

    def __init__(self, current_editor: str | None, parent=None):
        """Initialize editor configuration dialog.

        Args:
            current_editor: Currently configured editor path/command, or None
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_editor = current_editor
        self.selected_editor = None

        self.setWindowTitle("Configure Text Editor")
        self.setMinimumWidth(500)

        # Setup UI
        self.setup_ui()

        # Set initial selection based on current_editor
        self.set_initial_selection()

    def setup_ui(self):
        """Create dialog UI."""
        layout = QVBoxLayout(self)

        # Info label
        info = QLabel("Select your preferred text editor for viewing/editing tape files:")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addSpacing(10)

        # Radio button group
        self.button_group = QButtonGroup(self)

        # Option 1: System default
        self.system_radio = QRadioButton("System Default")
        self.button_group.addButton(self.system_radio)
        layout.addWidget(self.system_radio)

        system_desc = self._get_system_default_description()
        system_label = QLabel(system_desc)
        system_label.setStyleSheet("color: #757575; padding-left: 20px;")
        system_label.setWordWrap(True)
        layout.addWidget(system_label)

        layout.addSpacing(10)

        # Option 2: Preset editors
        self.preset_radio = QRadioButton("Common Editor")
        self.button_group.addButton(self.preset_radio)
        layout.addWidget(self.preset_radio)

        preset_layout = QHBoxLayout()
        preset_layout.addSpacing(20)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self._get_preset_editors())
        self.preset_combo.currentTextChanged.connect(lambda: self.preset_radio.setChecked(True))
        preset_layout.addWidget(self.preset_combo)

        layout.addLayout(preset_layout)

        layout.addSpacing(10)

        # Option 3: Custom command
        self.custom_radio = QRadioButton("Custom Command")
        self.button_group.addButton(self.custom_radio)
        layout.addWidget(self.custom_radio)

        custom_layout = QHBoxLayout()
        custom_layout.addSpacing(20)

        self.custom_edit = QLineEdit()
        self.custom_edit.setPlaceholderText("e.g., /usr/bin/gedit or notepad.exe")
        self.custom_edit.textChanged.connect(lambda: self.custom_radio.setChecked(True))
        custom_layout.addWidget(self.custom_edit)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_for_editor)
        custom_layout.addWidget(browse_button)

        layout.addLayout(custom_layout)

        # Add stretch
        layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _get_system_default_description(self) -> str:
        """Get description of system default editor."""
        system = platform.system()
        if system == "Linux":
            return "Uses xdg-open (opens in your default text editor)"
        elif system == "Windows":
            return "Uses notepad.exe (Windows Notepad)"
        elif system == "Darwin":
            return "Uses 'open -e' (macOS TextEdit)"
        else:
            return "Uses system default editor"

    def _get_preset_editors(self) -> list[str]:
        """Get list of common editors based on platform."""
        system = platform.system()

        if system == "Linux":
            return [
                "kate",
                "gedit",
                "geany",
                "vim",
                "emacs",
                "nano",
                "code",  # VS Code
                "subl",  # Sublime Text
            ]
        elif system == "Windows":
            return [
                "notepad.exe",
                "notepad++.exe",
                "code.exe",  # VS Code
                "sublime_text.exe",
            ]
        elif system == "Darwin":
            return [
                "TextEdit",
                "code",  # VS Code
                "subl",  # Sublime Text
                "vim",
                "emacs",
            ]
        else:
            return ["vim", "emacs", "nano"]

    def set_initial_selection(self):
        """Set initial selection based on current_editor."""
        if not self.current_editor:
            # No editor configured - select system default
            self.system_radio.setChecked(True)
            return

        # Check if it's a system default
        system_defaults = ["xdg-open", "notepad.exe", "open -e"]
        if self.current_editor in system_defaults:
            self.system_radio.setChecked(True)
            return

        # Check if it's in presets
        preset_editors = self._get_preset_editors()
        if self.current_editor in preset_editors:
            self.preset_radio.setChecked(True)
            index = preset_editors.index(self.current_editor)
            self.preset_combo.setCurrentIndex(index)
            return

        # Custom editor
        self.custom_radio.setChecked(True)
        self.custom_edit.setText(self.current_editor)

    def browse_for_editor(self):
        """Open file browser to select editor executable."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Text Editor", "", "Executables (*)"
        )

        if file_path:
            self.custom_edit.setText(file_path)
            self.custom_radio.setChecked(True)

    def accept(self):
        """Handle OK button click."""
        if self.system_radio.isChecked():
            # Return None to indicate system default should be used
            self.selected_editor = None
        elif self.preset_radio.isChecked():
            self.selected_editor = self.preset_combo.currentText()
        elif self.custom_radio.isChecked():
            custom = self.custom_edit.text().strip()
            if not custom:
                # Empty custom - treat as system default
                self.selected_editor = None
            else:
                self.selected_editor = custom
        else:
            # Shouldn't happen, but default to system
            self.selected_editor = None

        super().accept()

    def reject(self):
        """Handle Cancel button click."""
        self.selected_editor = None
        super().reject()

    @staticmethod
    def configure_editor(current_editor: str | None, parent=None) -> str | None:
        """Show editor configuration dialog and return selected editor.

        Args:
            current_editor: Currently configured editor path/command, or None
            parent: Parent widget

        Returns:
            Selected editor command, or None if cancelled or system default selected
        """
        dialog = EditorConfigDialog(current_editor, parent)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            return dialog.selected_editor
        else:
            # User cancelled - return special sentinel to indicate cancellation
            # We need to distinguish between "use system default" and "cancelled"
            # Return the original value unchanged
            return current_editor
