"""Dialog for displaying comprehensive tape file metadata."""

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)
from supertape.core.file.api import (
    FILE_TYPE_ASMSRC,
    FILE_TYPE_BASIC,
    FILE_TYPE_DATA,
    FILE_TYPE_MACHINE,
    TapeFile,
)

TYPE_NAMES = {
    FILE_TYPE_BASIC: "BASIC",
    FILE_TYPE_DATA: "DATA",
    FILE_TYPE_MACHINE: "MACHINE",
    FILE_TYPE_ASMSRC: "ASM",
}


class TapeInfoDialog(QDialog):
    """Dialog for displaying comprehensive tape file metadata."""

    def __init__(self, tape_file: TapeFile, parent=None):
        """Initialize tape info dialog.

        Args:
            tape_file: TapeFile object to display information about
            parent: Parent widget
        """
        super().__init__(parent)
        self.tape_file = tape_file
        self.setWindowTitle(f"Tape Information: {tape_file.fname}")
        self.setMinimumWidth(500)

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Create dialog UI."""
        layout = QVBoxLayout(self)

        # Create form layout for metadata
        form_layout = QFormLayout()

        # File name
        fname_edit = QLineEdit(self.tape_file.fname)
        fname_edit.setReadOnly(True)
        form_layout.addRow("File Name:", fname_edit)

        # File type
        ftype = self.tape_file.ftype
        type_name = TYPE_NAMES.get(ftype, "Unknown")
        type_str = f"0x{ftype:02X} ({type_name})"
        ftype_edit = QLineEdit(type_str)
        ftype_edit.setReadOnly(True)
        form_layout.addRow("File Type:", ftype_edit)

        # Data type
        fdatatype = self.tape_file.fdatatype
        datatype_str = f"0x{fdatatype:02X}"
        fdatatype_edit = QLineEdit(datatype_str)
        fdatatype_edit.setReadOnly(True)
        form_layout.addRow("Data Type:", fdatatype_edit)

        # Gap type
        fgap = self.tape_file.fgap
        gap_str = f"0x{fgap:02X}"
        fgap_edit = QLineEdit(gap_str)
        fgap_edit.setReadOnly(True)
        form_layout.addRow("Gap Type:", fgap_edit)

        # Start address
        fstartaddress = self.tape_file.fstartaddress
        start_str = f"${fstartaddress:04X} ({fstartaddress})"
        fstart_edit = QLineEdit(start_str)
        fstart_edit.setReadOnly(True)
        form_layout.addRow("Start Address:", fstart_edit)

        # Load address
        floadaddress = self.tape_file.floadaddress
        if floadaddress is not None:
            load_str = f"${floadaddress:04X} ({floadaddress})"
        else:
            load_str = "Not set"
        fload_edit = QLineEdit(load_str)
        fload_edit.setReadOnly(True)
        form_layout.addRow("Load Address:", fload_edit)

        # Body size
        body_size = len(self.tape_file.fbody)
        size_str = f"{body_size} bytes"
        size_edit = QLineEdit(size_str)
        size_edit.setReadOnly(True)
        form_layout.addRow("Body Size:", size_edit)

        # Number of blocks
        num_blocks = len(self.tape_file.blocks)
        blocks_str = f"{num_blocks} blocks"
        blocks_edit = QLineEdit(blocks_str)
        blocks_edit.setReadOnly(True)
        form_layout.addRow("Block Count:", blocks_edit)

        layout.addLayout(form_layout)

        # Block checksums (in text edit for multi-line)
        checksum_label = QLabel("Block Checksums:")
        layout.addWidget(checksum_label)

        checksum_text = QTextEdit()
        checksum_text.setReadOnly(True)
        checksum_text.setMaximumHeight(100)

        # Build checksum display
        checksum_info = []
        for idx, block in enumerate(self.tape_file.blocks):
            block_type_name = {0x00: "Header", 0x01: "Data", 0xFF: "EOF"}.get(
                block.type, f"0x{block.type:02X}"
            )
            checksum_info.append(f"Block {idx} ({block_type_name}): 0x{block.checksum:02X}")

        checksum_text.setPlainText("\n".join(checksum_info))
        layout.addWidget(checksum_text)

        # Copy to clipboard button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(copy_button)

        # OK button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def copy_to_clipboard(self):
        """Copy all metadata to clipboard."""
        ftype = self.tape_file.ftype
        type_name = TYPE_NAMES.get(ftype, "Unknown")
        floadaddress = self.tape_file.floadaddress

        text = f"""Tape File Information
======================
File Name: {self.tape_file.fname}
File Type: 0x{ftype:02X} ({type_name})
Data Type: 0x{self.tape_file.fdatatype:02X}
Gap Type: 0x{self.tape_file.fgap:02X}
Start Address: ${self.tape_file.fstartaddress:04X} ({self.tape_file.fstartaddress})
Load Address: {
    "$" + f"{floadaddress:04X} ({floadaddress})"
    if floadaddress is not None
    else "Not set"
}
Body Size: {len(self.tape_file.fbody)} bytes
Block Count: {len(self.tape_file.blocks)} blocks

Block Checksums:
"""
        for idx, block in enumerate(self.tape_file.blocks):
            block_type_name = {0x00: "Header", 0x01: "Data", 0xFF: "EOF"}.get(
                block.type, f"0x{block.type:02X}"
            )
            text += f"  Block {idx} ({block_type_name}): 0x{block.checksum:02X}\n"

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)

    @staticmethod
    def show_info(tape_file: TapeFile, parent=None):
        """Show tape information dialog.

        Args:
            tape_file: TapeFile object to display information about
            parent: Parent widget
        """
        dialog = TapeInfoDialog(tape_file, parent)
        dialog.exec()
