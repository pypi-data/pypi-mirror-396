"""Configuration management for Supertape GUI."""

from typing import Optional

from PySide6.QtCore import QSettings


class ConfigManager:
    """Manages application configuration using QSettings.

    Provides type-safe access to configuration values with platform-specific
    storage locations:
    - Linux: ~/.config/Supertape/Supertape GUI.conf
    - Windows: Registry HKEY_CURRENT_USER\\Software\\Supertape\\Supertape GUI
    - macOS: ~/Library/Preferences/org.supertape.Supertape GUI.plist
    """

    def __init__(self):
        """Initialize configuration manager with QSettings."""
        # Organization and application names determine storage location
        self.settings = QSettings("Supertape", "Supertape GUI")

    def get_repository_path(self) -> Optional[str]:
        """Get the configured repository folder path.

        Returns:
            Repository folder path as string, or None if not configured
        """
        value = self.settings.value("repository/path", None)
        # QSettings may return empty string, normalize to None
        return value if value else None

    def set_repository_path(self, path: Optional[str]) -> None:
        """Set the repository folder path.

        Args:
            path: Absolute path to repository folder, or None to clear
        """
        if path:
            self.settings.setValue("repository/path", path)
        else:
            self.clear_repository_path()

    def clear_repository_path(self) -> None:
        """Remove the repository path from configuration."""
        self.settings.remove("repository/path")

    def get_text_editor(self) -> Optional[str]:
        """Get configured text editor path/command.

        Returns:
            Text editor command as string, or None if not configured
        """
        value = self.settings.value("editor/text_editor", None)
        # QSettings may return empty string, normalize to None
        return value if value else None

    def set_text_editor(self, editor_path: Optional[str]) -> None:
        """Set text editor path/command.

        Args:
            editor_path: Editor command or path, or None to clear and use system default
        """
        if editor_path:
            self.settings.setValue("editor/text_editor", editor_path)
        else:
            self.settings.remove("editor/text_editor")
