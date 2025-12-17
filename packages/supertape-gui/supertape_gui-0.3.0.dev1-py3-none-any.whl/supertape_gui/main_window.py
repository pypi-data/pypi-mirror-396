"""Main window for Supertape GUI application."""

import os
import subprocess
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTemporaryDir, QThread, QUrl, Slot
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import file type constants and TapeFile
from supertape.core.file.api import (
    FILE_TYPE_ASMSRC,
    FILE_TYPE_BASIC,
    FILE_TYPE_DATA,
    FILE_TYPE_MACHINE,
    TapeFile,
)

# Import utilities
from .utils import ConfigManager, FileCompiler, PipelineState

# Import widgets
from .widgets import (
    AsmTypeDialog,
    BitsViewWidget,
    BlockIndicatorWidget,
    HexDumpWidget,
    TapeCollectionWidget,
    WaveformWidget,
)

# Import workers
from .workers import AudioInputWorker, AudioPlayerWorker


class MainWindow(QMainWindow):
    """Main application window for Supertape GUI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Supertape GUI")
        self.setMinimumSize(1200, 800)

        # Initialize pipeline state
        self.pipeline_state = PipelineState()

        # Configuration and repository
        self.config_manager = ConfigManager()

        # Create temporary directory for drag-and-drop exports
        self.temp_export_dir = QTemporaryDir()
        if not self.temp_export_dir.isValid():
            # Fallback to system temp if QTemporaryDir fails
            import tempfile

            self.temp_export_path = tempfile.mkdtemp(prefix="supertape_export_")
        else:
            self.temp_export_path = self.temp_export_dir.path()

        self.repository = None  # Repository instance if configured

        # Threading
        self.audio_thread = None
        self.audio_worker = None

        # State
        self.current_tape = None
        self.loaded_tapes: list["TapeFile"] = []

        # Initialize UI components
        self.setup_menubar()
        self.setup_ui()
        self.setup_statusbar()
        self.connect_signals()

        # Try to populate audio devices
        self.populate_devices()

        # Initialize repository from configuration
        self.initialize_repository()

    def setup_menubar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Tape File...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_tape_file)
        file_menu.addAction(open_action)

        # Repository submenu
        repository_menu = file_menu.addMenu("&Repository")

        select_repo_action = QAction("&Select Repository Folder...", self)
        select_repo_action.triggered.connect(self.select_repository_folder)
        repository_menu.addAction(select_repo_action)

        clear_repo_action = QAction("&Reset to Default Repository", self)
        clear_repo_action.triggered.connect(self.clear_repository)
        repository_menu.addAction(clear_repo_action)

        info_action = QAction("Repository &Info", self)
        info_action.triggered.connect(self.show_repository_info)
        repository_menu.addAction(info_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        devices_action = QAction("&Audio Devices", self)
        devices_action.triggered.connect(self.show_devices)
        tools_menu.addAction(devices_action)

        editor_action = QAction("Configure &Editor...", self)
        editor_action.triggered.connect(self.configure_editor)
        tools_menu.addAction(editor_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_ui(self):
        """Create the main UI layout with three-row monitoring design."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)

        # === ROW 0: Device selection and controls (compact) ===
        controls_layout = QHBoxLayout()

        # Device selection
        device_label = QLabel("Device:")
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(250)
        controls_layout.addWidget(device_label)
        controls_layout.addWidget(self.device_combo)

        controls_layout.addSpacing(20)

        # Control buttons (smaller)
        self.play_button = QPushButton("Play")
        self.play_button.setMinimumSize(80, 30)
        self.play_button.clicked.connect(self.on_play_clicked)
        self.play_button.setEnabled(False)  # Disabled until tape selected
        controls_layout.addWidget(self.play_button)

        self.record_button = QPushButton("Record")
        self.record_button.setMinimumSize(80, 30)
        self.record_button.clicked.connect(self.on_record_clicked)
        controls_layout.addWidget(self.record_button)

        self.listen_button = QPushButton("Listen")
        self.listen_button.setMinimumSize(80, 30)
        self.listen_button.clicked.connect(self.on_listen_clicked)
        controls_layout.addWidget(self.listen_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setMinimumSize(80, 30)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)

        controls_layout.addStretch()

        main_layout.addLayout(controls_layout)

        # === ROW 1: Input Pipeline Monitoring ===
        input_group = QGroupBox("Input Pipeline Monitoring")
        input_layout = QHBoxLayout(input_group)

        # Create input widgets
        self.input_waveform = WaveformWidget()
        self.input_bits_view = BitsViewWidget()
        self.input_hex_dump = HexDumpWidget()
        self.input_block_indicator = BlockIndicatorWidget()

        # Add to layout with stretch factors
        input_layout.addWidget(self.input_waveform, 2)
        input_layout.addWidget(self.input_bits_view, 1)
        input_layout.addWidget(self.input_hex_dump, 1)
        input_layout.addWidget(self.input_block_indicator, 1)

        # Set fixed height for row 1
        input_group.setMaximumHeight(180)

        main_layout.addWidget(input_group)

        # === ROW 2: Tape Collection ===
        tape_group = QGroupBox("Tape Collection")
        tape_layout = QVBoxLayout(tape_group)

        self.tape_collection = TapeCollectionWidget()  # Dynamic columns based on width
        self.tape_collection.set_temp_export_dir(self.temp_export_path)

        tape_layout.addWidget(self.tape_collection)

        main_layout.addWidget(tape_group)

        # === ROW 3: Output Pipeline Monitoring ===
        output_group = QGroupBox("Output Pipeline Monitoring")
        output_layout = QHBoxLayout(output_group)

        # Create output widgets (reversed order)
        self.output_block_indicator = BlockIndicatorWidget()
        self.output_hex_dump = HexDumpWidget()
        self.output_bits_view = BitsViewWidget()
        self.output_waveform = WaveformWidget()

        # Add to layout with stretch factors
        output_layout.addWidget(self.output_block_indicator, 1)
        output_layout.addWidget(self.output_hex_dump, 1)
        output_layout.addWidget(self.output_bits_view, 1)
        output_layout.addWidget(self.output_waveform, 2)

        # Set fixed height for row 3
        output_group.setMaximumHeight(180)

        main_layout.addWidget(output_group)

        # === Console Output (smaller, at bottom) ===
        console_label = QLabel("Console:")
        main_layout.addWidget(console_label)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMaximumHeight(100)
        main_layout.addWidget(self.console_output)

    def setup_statusbar(self):
        """Create the status bar."""
        statusbar = self.statusBar()
        statusbar.showMessage("Ready")

    def connect_signals(self):
        """Connect PipelineState signals to widget slots."""
        # Input pipeline connections
        self.pipeline_state.input_audio_data.connect(self.input_waveform.update_data)
        self.pipeline_state.input_bit_data.connect(self.input_bits_view.append_bit)
        self.pipeline_state.input_byte_data.connect(self.input_hex_dump.append_byte)
        self.pipeline_state.input_block_data.connect(self.input_block_indicator.update_block)
        self.pipeline_state.tape_received.connect(self.on_tape_received)

        # Output pipeline connections
        self.pipeline_state.output_audio_data.connect(self.output_waveform.update_data)
        self.pipeline_state.output_bit_data.connect(self.output_bits_view.append_bit)
        self.pipeline_state.output_byte_data.connect(self.output_hex_dump.append_byte)
        self.pipeline_state.output_block_data.connect(self.output_block_indicator.update_block)

        # Tape collection
        self.tape_collection.file_dropped.connect(self.on_files_dropped)

        # Tape action connections
        self.tape_collection.tape_double_clicked.connect(self.on_tape_double_clicked)
        self.tape_collection.tape_play_requested.connect(self.on_tape_play_requested)
        self.tape_collection.tape_edit_requested.connect(self.on_tape_edit_requested)
        self.tape_collection.tape_delete_requested.connect(self.on_tape_delete_requested)
        self.tape_collection.tape_info_requested.connect(self.on_tape_info_requested)
        self.tape_collection.tape_history_requested.connect(self.on_tape_history_requested)

        # Pipeline state changes
        self.pipeline_state.error_occurred.connect(self.on_error)
        self.pipeline_state.listening_started.connect(
            lambda: self.console_output.append(
                "<span style='color: green;'>Listening started...</span>"
            )
        )
        self.pipeline_state.listening_stopped.connect(
            lambda: self.console_output.append(
                "<span style='color: orange;'>Listening stopped</span>"
            )
        )
        self.pipeline_state.playing_started.connect(
            lambda: self.console_output.append(
                "<span style='color: green;'>Playback started...</span>"
            )
        )
        self.pipeline_state.playing_stopped.connect(
            lambda: self.console_output.append(
                "<span style='color: orange;'>Playback stopped</span>"
            )
        )

    def populate_devices(self):
        """Populate the audio device combo box."""
        self.console_output.append("Initializing audio devices...")

        try:
            # Import supertape's audio device singleton
            from supertape.core.audio.device import get_device

            # Get the audio device singleton
            device = get_device()

            # Get list of audio devices
            # Returns list[list[int | str]] where each item is [index, name]
            devices = device.get_audio_devices()

            self.device_combo.clear()

            if not devices:
                self.device_combo.addItem("No devices available")
                self.console_output.append(
                    "<span style='color: orange;'>No audio devices found</span>"
                )
                self.statusBar().showMessage("No audio devices available")
                return

            # Add devices to combo box
            for device_info in devices:
                device_index = device_info[0]  # Device ID
                device_name = device_info[1]  # Device name with channel info
                self.device_combo.addItem(device_name, device_index)

            self.console_output.append(
                f"<span style='color: green;'>Found {len(devices)} audio device(s)</span>"
            )
            self.statusBar().showMessage(f"{len(devices)} audio device(s) available")

        except ImportError as e:
            self.console_output.append(
                f"<span style='color: orange;'>Warning: Could not import supertape: {e}</span>"
            )
            self.console_output.append("Please install supertape: pip install supertape")
            self.device_combo.addItem("No devices available")
            self.statusBar().showMessage("Supertape not installed")

        except Exception as e:
            self.console_output.append(
                f"<span style='color: red;'>Error listing audio devices: {e}</span>"
            )
            self.device_combo.addItem("Error loading devices")
            self.statusBar().showMessage("Error loading devices")

    def get_tape_file_path(self, tape: TapeFile) -> Path:
        """Get .k7 file path for a tape file.

        Args:
            tape: TapeFile object

        Returns:
            Path to .k7 file in repository
        """
        if not self.repository:
            raise ValueError("No repository configured")

        safe_name = "".join(
            c for c in tape.fname.upper() if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        if not safe_name:
            safe_name = f"tape_{id(tape)}"

        return Path(self.repository.repository_dir) / f"{safe_name}.k7"

    def _get_tape_timestamp_from_repo(self, tape_file: TapeFile) -> Optional[int]:
        """Get timestamp from repository history for a tape file.

        Args:
            tape_file: TapeFile to get timestamp for

        Returns:
            Unix timestamp of most recent version, or None if unavailable
        """
        if not self.repository:
            return None
        try:
            versions = self.repository.get_tape_file_versions(tape_file.fname)
            return versions[-1].timestamp if versions else None
        except Exception:
            return None

    def get_configured_editor(self) -> str:
        """Get configured or system default text editor.

        Returns:
            Editor command string
        """
        editor = self.config_manager.get_text_editor()
        if editor:
            return str(editor)

        import platform

        system = platform.system()
        if system == "Linux":
            return "xdg-open"
        elif system == "Windows":
            return "notepad.exe"
        elif system == "Darwin":
            return "open -e"
        else:
            return "xdg-open"

    def export_tape_as_text(self, tape: TapeFile) -> Optional[Path]:
        """Export tape body as text file for editing.

        For BASIC/ASMSRC files: exports as text
        For MACHINE files: disassembles to assembly source
        For DATA files: returns None (cannot edit)

        Args:
            tape: TapeFile to export

        Returns:
            Path to temporary text file, or None if cannot be edited
        """
        import tempfile

        from supertape.core.disasm.m6803 import disassemble

        if tape.ftype == FILE_TYPE_BASIC:
            extension = ".bas"
            fd, temp_path = tempfile.mkstemp(suffix=extension, prefix=f"{tape.fname}_")
            try:
                with os.fdopen(fd, "w", encoding="latin-1") as f:
                    text = "".join(chr(b) for b in tape.fbody)
                    f.write(text)
                return Path(temp_path)
            except Exception as e:
                self.console_output.append(
                    f"<span style='color: red;'>Failed to export BASIC: {e}</span>"
                )
                return None

        elif tape.ftype == FILE_TYPE_ASMSRC:
            extension = ".asm"
            fd, temp_path = tempfile.mkstemp(suffix=extension, prefix=f"{tape.fname}_")
            try:
                with os.fdopen(fd, "w", encoding="latin-1") as f:
                    text = "".join(chr(b) for b in tape.fbody)
                    f.write(text)
                return Path(temp_path)
            except Exception as e:
                self.console_output.append(
                    f"<span style='color: red;'>Failed to export assembly: {e}</span>"
                )
                return None

        elif tape.ftype == FILE_TYPE_MACHINE:
            # Disassemble machine code
            extension = ".asm"
            fd, temp_path = tempfile.mkstemp(suffix=extension, prefix=f"{tape.fname}_disasm_")
            try:
                # Disassemble
                start_addr = tape.floadaddress if hasattr(tape, "floadaddress") else 0
                if start_addr is None:
                    start_addr = 0
                disasm_lines = disassemble(list(tape.fbody), start_addr)

                with os.fdopen(fd, "w") as f:
                    f.write(f"; Disassembly of {tape.fname}\n")
                    f.write(f"; Load address: ${start_addr:04X}\n")
                    f.write(f"; Size: {len(tape.fbody)} bytes\n")
                    f.write(";\n")
                    f.write("\n".join(disasm_lines))

                return Path(temp_path)
            except Exception as e:
                self.console_output.append(
                    f"<span style='color: red;'>Failed to disassemble: {e}</span>"
                )
                return None

        else:
            # DATA files cannot be edited as text
            return None

    @Slot()
    def on_play_clicked(self):
        """Handle play button click."""
        if self.current_tape is None:
            self.console_output.append(
                "<span style='color: orange;'>No tape selected to play</span>"
            )
            return

        if self.audio_thread is not None:
            self.console_output.append(
                "<span style='color: orange;'>Audio operation already in progress</span>"
            )
            return

        # Clear output widgets
        self.clear_output_widgets()

        # Get selected device
        device = self.device_combo.currentData()

        # Create thread and worker
        self.audio_thread = QThread()
        self.audio_worker = AudioPlayerWorker(self.current_tape, device, self.pipeline_state)
        self.audio_worker.moveToThread(self.audio_thread)

        # Connect signals
        self.audio_thread.started.connect(self.audio_worker.play)
        self.audio_worker.finished.connect(self.audio_thread.quit)
        self.audio_worker.finished.connect(self.on_audio_finished)
        self.audio_worker.error.connect(self.on_error)
        self.audio_worker.progress.connect(self.on_progress)

        # Update UI
        self.set_buttons_during_operation(False, False, False, True)
        self.console_output.append(
            f"<span style='color: blue;'>Playing tape: {self.current_tape.fname}</span>"
        )
        self.statusBar().showMessage("Playing tape...")

        # Start thread
        self.audio_thread.start()

    @Slot()
    def on_record_clicked(self):
        """Handle record button click."""
        self.console_output.append(
            "<span style='color: orange;'>Record functionality not yet implemented</span>"
        )
        self.statusBar().showMessage("Record functionality coming soon...")

    @Slot()
    def on_listen_clicked(self):
        """Handle listen button click."""
        if self.audio_thread is not None:
            self.console_output.append(
                "<span style='color: orange;'>Audio operation already in progress</span>"
            )
            return

        # Clear input widgets
        self.clear_input_widgets()

        # Get selected device
        device = self.device_combo.currentData()

        # Create thread and worker
        self.audio_thread = QThread()
        self.audio_worker = AudioInputWorker(device, self.pipeline_state)
        self.audio_worker.moveToThread(self.audio_thread)

        # Connect signals
        self.audio_thread.started.connect(self.audio_worker.start_listening)
        self.audio_worker.finished.connect(self.audio_thread.quit)
        self.audio_worker.finished.connect(self.on_audio_finished)
        self.audio_worker.error.connect(self.on_error)

        # Update UI
        self.set_buttons_during_operation(False, False, False, True)
        self.console_output.append("<span style='color: blue;'>Starting listen mode...</span>")
        self.statusBar().showMessage("Listening for tape data...")

        # Start thread
        self.audio_thread.start()

    @Slot()
    def on_stop_clicked(self):
        """Handle stop button click."""
        if self.audio_worker is not None:
            self.console_output.append("<span style='color: blue;'>Stopping...</span>")
            self.audio_worker.stop()

    def on_audio_finished(self):
        """Handle audio operation finished."""
        # Clean up thread
        if self.audio_thread is not None:
            self.audio_thread.wait()
            self.audio_thread = None
        self.audio_worker = None

        # Re-enable buttons
        has_tape = self.current_tape is not None
        self.set_buttons_during_operation(has_tape, True, True, False)
        self.statusBar().showMessage("Ready")

    def initialize_repository(self):
        """Initialize repository with default or configured path on startup."""
        repo_path = self.config_manager.get_repository_path()

        try:
            # Import repository class
            from supertape.core.repository.dulwich_repo import DulwichRepository

            # Always create repository (None → default ~/.supertape/tapes)
            self.repository = DulwichRepository(
                repository_dir=repo_path, observers=[GuiRepositoryObserver(self)]
            )

            # Set repository on tape collection for timestamp lookups
            self.tape_collection.set_repository(self.repository)

            # Load all tapes from repository with timestamps
            tapes = self.repository.get_tape_files()
            for tape in tapes:
                timestamp = self._get_tape_timestamp_from_repo(tape)
                self.tape_collection.add_tape(tape, timestamp)
                self.loaded_tapes.append(tape)

            # Status message - use actual repository path
            location = "custom" if repo_path else "default"
            message = f"Repository: {self.repository.repository_dir} ({location})"

            if tapes:
                self.console_output.append(
                    f"<span style='color: green;'>"
                    f"Loaded {len(tapes)} tape(s) - {message}"
                    f"</span>"
                )

            self.statusBar().showMessage(message)

        except Exception as e:
            # Graceful degradation - don't crash app
            # Use generic Exception to catch both RepositoryError and ImportError
            self.console_output.append(
                f"<span style='color: orange;'>"
                f"Warning: Could not initialize repository: {e}"
                f"</span>"
            )
            # Don't fail startup, just disable repository
            self.repository = None

    @Slot()
    def select_repository_folder(self):
        """Select repository folder via dialog."""
        # Get initial directory from config or default
        current_path = self.config_manager.get_repository_path()
        initial_dir = current_path if current_path else str(Path.home())

        folder = QFileDialog.getExistingDirectory(
            self, "Select Repository Folder", initial_dir, QFileDialog.Option.ShowDirsOnly
        )

        if folder:
            try:
                # Import repository class
                from supertape.core.repository.dulwich_repo import DulwichRepository

                # Save to config
                self.config_manager.set_repository_path(folder)

                # Initialize new repository
                self.repository = DulwichRepository(
                    repository_dir=folder, observers=[GuiRepositoryObserver(self)]
                )

                # Set repository on tape collection
                self.tape_collection.set_repository(self.repository)

                # Load existing tapes from repository (don't duplicate)
                repo_tapes = self.repository.get_tape_files()
                for tape in repo_tapes:
                    # Check if already loaded
                    if not any(t.fname.upper() == tape.fname.upper() for t in self.loaded_tapes):
                        timestamp = self._get_tape_timestamp_from_repo(tape)
                        self.tape_collection.add_tape(tape, timestamp)
                        self.loaded_tapes.append(tape)

                self.console_output.append(
                    f"<span style='color: green;'>" f"Repository configured: {folder}" f"</span>"
                )
                self.statusBar().showMessage(f"Repository: {folder}")

            except Exception as e:
                self.console_output.append(
                    f"<span style='color: red;'>" f"Failed to configure repository: {e}" f"</span>"
                )
                QMessageBox.critical(
                    self, "Repository Error", f"Failed to configure repository:\n{e}"
                )

    @Slot()
    def clear_repository(self):
        """Reset repository to default location."""
        reply = QMessageBox.question(
            self,
            "Reset Repository",
            "This will reset to the default repository location (~/.supertape/tapes).\n"
            "Custom repository files will remain on disk.\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.clear_repository_path()

            # Clear current tapes
            self.tape_collection.clear()
            self.loaded_tapes.clear()
            self.current_tape = None

            # Reinitialize with default
            self.initialize_repository()

            self.console_output.append(
                "<span style='color: green;'>Repository reset to default location</span>"
            )

    @Slot()
    def show_repository_info(self):
        """Show repository information dialog."""
        if not self.repository:
            QMessageBox.information(
                self,
                "Repository Info",
                "No repository configured.\n\n"
                "Use 'File > Repository > Select Repository Folder...' to configure.",
            )
            return

        try:
            info = self.repository.get_repository_info()

            # Format storage size
            size_kb = info.storage_size / 1024
            size_str = f"{size_kb:.2f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"

            QMessageBox.information(
                self,
                "Repository Info",
                f"Repository Type: {info.type}\n"
                f"Location: {info.path}\n"
                f"File Count: {info.file_count}\n"
                f"Storage Size: {size_str}",
            )

        except Exception as e:
            QMessageBox.critical(self, "Repository Error", f"Failed to get repository info:\n{e}")

    @Slot()
    def configure_editor(self):
        """Show editor configuration dialog."""
        from .widgets import EditorConfigDialog

        current_editor = self.config_manager.get_text_editor()
        new_editor = EditorConfigDialog.configure_editor(current_editor, self)

        # Check if user cancelled (new_editor == current_editor)
        if new_editor != current_editor:
            self.config_manager.set_text_editor(new_editor)
            if new_editor:
                self.console_output.append(
                    f"<span style='color: green;'>Editor configured: {new_editor}</span>"
                )
            else:
                self.console_output.append(
                    "<span style='color: green;'>Editor reset to system default</span>"
                )

    @Slot()
    def open_tape_file(self):
        """Open a tape file dialog."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Tape File", "", "Tape Files (*.k7 *.bas *.asm *.c);;All Files (*)"
        )
        if filename:
            self.import_file(filename)

    def import_file(self, filename: str):
        """Import a single file (from dialog or drag-drop).

        Args:
            filename: Path to file to import
        """
        # Status bar feedback
        self.statusBar().showMessage(f"Importing {Path(filename).name}...")

        # For .asm files, ask user about mode
        asm_as_machine = False
        if Path(filename).suffix.lower() == ".asm":
            mode = AsmTypeDialog.ask_mode(Path(filename).name, self)
            if mode is None:
                self.statusBar().showMessage("Import cancelled")
                return
            asm_as_machine = mode == "machine"

        # Compile file
        result = FileCompiler.compile_file(filename, asm_as_machine)

        # Handle errors
        if not result.success:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import {Path(filename).name}:\n\n{result.error_message}",
            )
            self.statusBar().showMessage("Import failed")
            self.console_output.append(
                f"<span style='color: red;'>Import failed: {result.error_message}</span>"
            )
            return

        tape_file = result.tape_file
        assert tape_file is not None  # Guaranteed by result.success == True

        # Check for duplicates
        if any(t.fname.upper() == tape_file.fname.upper() for t in self.loaded_tapes):
            QMessageBox.warning(
                self, "Duplicate File", f"Tape '{tape_file.fname}' is already loaded."
            )
            self.statusBar().showMessage("Duplicate tape")
            return

        # Add to loaded tapes list FIRST to prevent observer duplication
        self.loaded_tapes.append(tape_file)

        # Auto-save to repository if available
        timestamp = None
        if self.repository:
            try:
                self.repository.add_tape_file(tape_file)
                timestamp = self._get_tape_timestamp_from_repo(tape_file)
                self.console_output.append(
                    f"<span style='color: green;'>Imported and saved: {tape_file.fname}</span>"
                )
                self.statusBar().showMessage(f"Imported and saved: {tape_file.fname}")
            except Exception as e:
                self.console_output.append(
                    f"<span style='color: orange;'>"
                    f"Imported {tape_file.fname} (not saved to repository: {e})"
                    f"</span>"
                )
                self.statusBar().showMessage(f"Imported: {tape_file.fname}")

        # Add to collection with timestamp
        # Observer won't duplicate because tape is already in loaded_tapes
        self.tape_collection.add_tape(tape_file, timestamp)
        # Note: else branch removed - if repository is None, graceful degradation already occurred

    @Slot(list)
    def on_files_dropped(self, files: list[str]):
        """Handle files dropped on tape collection.

        Args:
            files: List of file paths that were dropped
        """
        if len(files) == 1:
            # Single file: show ASM dialog if needed
            self.import_file(files[0])
        else:
            # Multiple files: batch import, default ASM to MACHINE
            success_count = 0
            failed_count = 0

            for filename in files:
                result = FileCompiler.compile_file(filename, asm_as_machine=True)

                if result.success:
                    tape_file = result.tape_file
                    assert tape_file is not None  # Guaranteed by result.success == True

                    # Skip duplicates
                    if any(t.fname.upper() == tape_file.fname.upper() for t in self.loaded_tapes):
                        continue

                    # Add to loaded tapes list FIRST to prevent observer duplication
                    self.loaded_tapes.append(tape_file)

                    # Auto-save to repository
                    timestamp = None
                    if self.repository:
                        try:
                            self.repository.add_tape_file(tape_file)
                            timestamp = self._get_tape_timestamp_from_repo(tape_file)
                        except Exception:
                            pass  # Silent fail for batch

                    # Add to collection with timestamp
                    # Observer won't duplicate because tape is already in loaded_tapes
                    self.tape_collection.add_tape(tape_file, timestamp)

                    success_count += 1
                else:
                    failed_count += 1

            # Summary message
            if success_count > 0:
                self.console_output.append(
                    f"<span style='color: green;'>Imported {success_count} file(s)</span>"
                )
            if failed_count > 0:
                self.console_output.append(
                    f"<span style='color: orange;'>"
                    f"Failed to import {failed_count} file(s)"
                    f"</span>"
                )

            self.statusBar().showMessage(f"Imported {success_count} file(s), {failed_count} failed")

    @Slot()
    def show_devices(self):
        """Show audio devices dialog."""
        self.populate_devices()

    @Slot()
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Supertape GUI",
            "<h3>Supertape GUI</h3>"
            "<p>Multi-platform graphical interface for supertape</p>"
            "<p>Duplex audio communication with vintage computers<br>"
            "Tandy MC-10 and Matra Alice 4k/32/90</p>"
            "<p>Version 0.1.0</p>",
        )

    @Slot(object)
    def on_tape_double_clicked(self, tape_file):
        """Handle double-click on tape - select and play.

        Args:
            tape_file: TapeFile that was double-clicked
        """
        self.current_tape = tape_file
        self.on_play_clicked()

    @Slot(object)
    def on_tape_play_requested(self, tape_file):
        """Handle play request from context menu.

        Args:
            tape_file: TapeFile to play
        """
        self.current_tape = tape_file
        self.play_button.setEnabled(True)
        self.on_play_clicked()

    @Slot(object)
    def on_tape_edit_requested(self, tape_file):
        """Handle edit request - open in external editor.

        Args:
            tape_file: TapeFile to edit
        """
        # Try to export as text (handles BASIC, ASMSRC, and MACHINE via disassembly)
        temp_path = self.export_tape_as_text(tape_file)

        if not temp_path:
            # DATA files or export failed
            if tape_file.ftype == FILE_TYPE_DATA:
                reply = QMessageBox.question(
                    self,
                    "Data File",
                    f"{tape_file.fname} is a DATA file (type 0x{tape_file.ftype:02X}).\n\n"
                    "Data files cannot be edited as text.\n"
                    "Open the .k7 file in system default application instead?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.No:
                    return

                try:
                    k7_path = self.get_tape_file_path(tape_file)
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(k7_path)))
                    self.console_output.append(
                        f"<span style='color: green;'>Opened {tape_file.fname}.k7</span>"
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")
            return

        # Successfully exported - open in editor
        editor = self.get_configured_editor()

        try:
            if editor in ("xdg-open", "open -e"):
                subprocess.Popen([editor.split()[0], str(temp_path)])
            else:
                subprocess.Popen([editor, str(temp_path)])

            # Show different message for disassembled files
            if tape_file.ftype == FILE_TYPE_MACHINE:
                action = "disassembled and opened"
            else:
                action = "opened"

            self.console_output.append(
                f"<span style='color: green;'>{action.capitalize()} "
                f"{tape_file.fname} in {editor}</span>"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Editor Error",
                f"Failed to open editor:\n{e}\n\n"
                f"Configure editor in Tools > Configure Editor...",
            )

    @Slot(object)
    def on_tape_delete_requested(self, tape_file):
        """Handle delete request - remove from repository.

        Args:
            tape_file: TapeFile to delete
        """
        if not self.repository:
            QMessageBox.warning(self, "No Repository", "Cannot delete - no repository configured.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Tape",
            f"Delete '{tape_file.fname}' from repository?\n\n"
            f"This will create a deletion commit in git.\n"
            f"The file can be recovered from git history.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repository.remove_tape_file(tape_file)

                for idx, tape in enumerate(self.loaded_tapes):
                    if tape.fname.upper() == tape_file.fname.upper():
                        self.loaded_tapes.pop(idx)
                        self.tape_collection.remove_tape(idx)
                        break

                if self.current_tape and self.current_tape.fname.upper() == tape_file.fname.upper():
                    self.current_tape = None
                    self.play_button.setEnabled(False)

                self.console_output.append(
                    f"<span style='color: green;'>Deleted tape: {tape_file.fname}</span>"
                )
                self.statusBar().showMessage(f"Deleted: {tape_file.fname}")

            except Exception as e:
                self.console_output.append(f"<span style='color: red;'>Delete failed: {e}</span>")
                QMessageBox.critical(self, "Delete Error", f"Failed to delete tape:\n{e}")

    @Slot(object)
    def on_tape_info_requested(self, tape_file):
        """Handle info request - show metadata dialog.

        Args:
            tape_file: TapeFile to show information for
        """
        from .widgets import TapeInfoDialog

        TapeInfoDialog.show_info(tape_file, self)

    @Slot(object)
    def on_tape_history_requested(self, tape_file):
        """Handle history request - show git history dialog.

        Args:
            tape_file: TapeFile to show history for
        """
        if not self.repository:
            QMessageBox.information(
                self,
                "No Repository",
                "Git history is only available for tapes in a repository.",
            )
            return

        try:
            from .widgets import TapeHistoryDialog

            TapeHistoryDialog.show_history(tape_file, self.repository, self)
        except Exception as e:
            QMessageBox.critical(self, "History Error", f"Failed to load history:\n{e}")

    @Slot(object)
    def on_tape_received(self, tape_file):
        """Handle tape file received from listening.

        Args:
            tape_file: Received TapeFile object
        """
        # Auto-save to repository if available
        timestamp = None
        if self.repository:
            try:
                self.repository.add_tape_file(tape_file)
                timestamp = self._get_tape_timestamp_from_repo(tape_file)
                self.console_output.append(
                    f"<span style='color: green;'>"
                    f"Received and saved tape: {tape_file.fname}"
                    f"</span>"
                )
            except Exception as e:
                self.console_output.append(
                    f"<span style='color: orange;'>"
                    f"Received tape: {tape_file.fname} "
                    f"(not saved to repository: {e})"
                    f"</span>"
                )

        # Add to collection (if not already via observer)
        if not any(t.fname.upper() == tape_file.fname.upper() for t in self.loaded_tapes):
            self.tape_collection.add_tape(tape_file, timestamp)
            self.loaded_tapes.append(tape_file)

        self.statusBar().showMessage(f"Received: {tape_file.fname}")

    @Slot(str)
    def on_error(self, error_message):
        """Handle error from workers.

        Args:
            error_message: Error message string
        """
        self.console_output.append(f"<span style='color: red;'>Error: {error_message}</span>")
        self.statusBar().showMessage(f"Error: {error_message}")

    @Slot(int)
    def on_progress(self, percent):
        """Handle progress update.

        Args:
            percent: Progress percentage (0-100)
        """
        self.statusBar().showMessage(f"Progress: {percent}%")

    def set_buttons_during_operation(
        self, play_enabled, record_enabled, listen_enabled, stop_enabled
    ):
        """Set button enabled states during audio operations.

        Args:
            play_enabled: Enable play button
            record_enabled: Enable record button
            listen_enabled: Enable listen button
            stop_enabled: Enable stop button
        """
        self.play_button.setEnabled(play_enabled)
        self.record_button.setEnabled(record_enabled)
        self.listen_button.setEnabled(listen_enabled)
        self.stop_button.setEnabled(stop_enabled)

    def clear_input_widgets(self):
        """Clear all input pipeline widgets."""
        self.input_waveform.clear()
        self.input_bits_view.clear()
        self.input_hex_dump.clear()
        self.input_block_indicator.clear()

    def clear_output_widgets(self):
        """Clear all output pipeline widgets."""
        self.output_waveform.clear()
        self.output_bits_view.clear()
        self.output_hex_dump.clear()
        self.output_block_indicator.clear()


class GuiRepositoryObserver:
    """Observer for repository events to keep GUI in sync.

    This observer monitors repository changes and updates the GUI tape collection
    accordingly. It handles external additions and removals (not from GUI).
    """

    def __init__(self, main_window: MainWindow):
        """Initialize observer with reference to main window.

        Args:
            main_window: MainWindow instance to update
        """
        self.main_window = main_window

    def file_added(self, file) -> None:
        """Called when a file is added to the repository.

        This handles external additions (not from GUI).

        Args:
            file: TapeFile that was added
        """
        # Only add if not already in collection
        if not any(t.fname.upper() == file.fname.upper() for t in self.main_window.loaded_tapes):
            timestamp = self.main_window._get_tape_timestamp_from_repo(file)
            self.main_window.tape_collection.add_tape(file, timestamp)
            self.main_window.loaded_tapes.append(file)

    def file_removed(self, file) -> None:
        """Called when a file is removed from the repository.

        This handles external removals (not from GUI).

        Args:
            file: TapeFile that was removed
        """
        # Find and remove from collection
        for idx, tape in enumerate(self.main_window.loaded_tapes):
            if tape.fname.upper() == file.fname.upper():
                self.main_window.loaded_tapes.pop(idx)
                self.main_window.tape_collection.remove_tape(idx)
                break
