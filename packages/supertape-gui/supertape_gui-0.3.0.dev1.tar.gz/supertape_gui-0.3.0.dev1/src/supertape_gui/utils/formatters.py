"""Formatting utilities for hex dumps and bit streams."""


def format_hex_line(offset: int, byte_values: list[int], width: int = 16) -> str:
    """Format a line of hex dump output.

    Creates traditional hex dump format:
    0000: 48 45 4C 4C 4F 20 57 4F 52 4C 44 00 00 00 00 00  HELLO WORLD.....

    Args:
        offset: Byte offset for this line
        byte_values: List of byte values (0-255)
        width: Number of bytes per line (default 16)

    Returns:
        Formatted hex dump line
    """
    # Format offset (4 hex digits)
    line = f"{offset:04X}: "

    # Format hex bytes with space separation
    hex_part = " ".join(f"{b:02X}" for b in byte_values)
    # Pad to fixed width if needed
    hex_part = hex_part.ljust(width * 3 - 1)
    line += hex_part + "  "

    # Format ASCII representation
    ascii_part = ""
    for b in byte_values:
        if 32 <= b <= 126:  # Printable ASCII
            ascii_part += chr(b)
        else:
            ascii_part += "."

    line += ascii_part
    return line


def format_bit_stream(bit_char: str) -> tuple[str, str]:
    """Format a bit character with color coding.

    Args:
        bit_char: '0', '1', or '-' (invalid/sync)

    Returns:
        Tuple of (html_formatted_char, color)
    """
    color_map = {
        "0": "#4A90E2",  # Blue
        "1": "#50C878",  # Green
        "-": "#9E9E9E",  # Gray
    }

    color = color_map.get(bit_char, "#000000")  # Black for unknown
    html = f'<span style="color: {color};">{bit_char}</span>'

    return html, color


def bytes_to_hex_string(byte_values: list[int]) -> str:
    """Convert list of bytes to hex string.

    Args:
        byte_values: List of byte values (0-255)

    Returns:
        Hex string like "48656C6C6F"
    """
    return "".join(f"{b:02X}" for b in byte_values)


def hex_string_to_bytes(hex_str: str) -> list[int]:
    """Convert hex string to list of bytes.

    Args:
        hex_str: Hex string like "48656C6C6F"

    Returns:
        List of byte values
    """
    # Remove spaces and convert pairs of hex digits
    hex_str = hex_str.replace(" ", "")
    return [int(hex_str[i : i + 2], 16) for i in range(0, len(hex_str), 2)]
