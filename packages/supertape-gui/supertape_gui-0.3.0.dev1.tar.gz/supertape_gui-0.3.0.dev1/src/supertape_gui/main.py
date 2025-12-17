"""Main entry point for Supertape GUI application."""

import argparse
import sys
from importlib.metadata import version
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from supertape_gui.main_window import MainWindow


def get_version():
    """Get version from package metadata."""
    try:
        return version("supertape-gui")
    except Exception:
        return "unknown"


def main():
    """Initialize and run the Supertape GUI application."""
    # Parse command line arguments
    app_version = get_version()
    parser = argparse.ArgumentParser(
        prog="supertape-gui",
        description=(
            "Multi-platform GUI for supertape - "
            "duplex audio communication with vintage computers"
        ),
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {app_version}")

    # Parse args (will handle -h/--help automatically)
    parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("Supertape GUI")
    app.setOrganizationName("Supertape")
    app.setApplicationVersion(app_version)

    # Set application icon
    icon_dir = Path(__file__).parent / "resources" / "icons"
    app_icon = QIcon()

    # Add multiple sizes for better rendering across different contexts
    icon_sizes = [16, 32, 48, 64, 128, 256]
    for size in icon_sizes:
        icon_path = icon_dir / f"app_icon_{size}.png"
        if icon_path.exists():
            app_icon.addFile(str(icon_path))

    # Fallback to SVG if PNG files not found
    svg_icon_path = icon_dir / "app_icon.svg"
    if not app_icon.availableSizes() and svg_icon_path.exists():
        app_icon.addFile(str(svg_icon_path))

    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    # Create and show main window
    window = MainWindow()

    # Also set icon on main window
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)

    window.show()

    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
