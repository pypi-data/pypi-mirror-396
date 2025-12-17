# Supertape GUI

Multi-platform graphical interface for [supertape](https://pypi.org/project/supertape/) - duplex audio communication with vintage computers (Tandy MC-10 and Matra Alice 4k/32/90).

## Features

- Cross-platform GUI (Windows, macOS, Linux)
- Direct integration with supertape Python library
- Live audio monitoring with VU meters (planned)
- Waveform visualization (planned)
- Audio device selection
- Play, record, and listen modes

## Installation

### From Source

1. Clone this repository
2. Install dependencies using Poetry:

```bash
poetry install
```

3. Run the application:

```bash
poetry run supertape-gui
```

### Development

Run in development mode:

```bash
python -m supertape_gui.main
```

### Building Standalone Executables

Use PyInstaller to build standalone executables:

```bash
poetry run pyinstaller build/supertape-gui.spec
```

## Requirements

- Python 3.11+
- PySide6 (Qt for Python)
- supertape package
- PyQtGraph for visualization
- QDarkStyle for theming

## Technology Stack

- **GUI Framework**: PySide6 (Qt for Python)
- **Visualization**: PyQtGraph
- **Audio Backend**: supertape (PyAudio)
- **Packaging**: PyInstaller

## Project Structure

```
supertape-gui/
├── supertape_gui/
│   ├── main.py              # Entry point
│   ├── main_window.py       # Main window
│   ├── widgets/             # Custom widgets
│   ├── workers/             # Background threads
│   ├── utils/               # Utilities
│   └── resources/           # Icons, themes
├── tests/                   # Test suite
├── build/                   # PyInstaller specs
└── pyproject.toml           # Poetry config
```

## License

TBD

## Contributing

Contributions welcome! Please feel free to submit pull requests.
