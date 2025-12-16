"""
Colored console output utilities for CLI interface.

This module provides cross-platform colored output functionality using colorama,
matching the WriteColored pattern from the C# implementation.
"""

from enum import Enum

try:
    from colorama import Fore, Style
    from colorama import init as colorama_init

    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class Color(Enum):
    """Console colors matching C# ConsoleColor enum."""

    BLACK = "BLACK"
    DARK_BLUE = "DARK_BLUE"
    DARK_GREEN = "DARK_GREEN"
    DARK_CYAN = "DARK_CYAN"
    DARK_RED = "DARK_RED"
    DARK_MAGENTA = "DARK_MAGENTA"
    DARK_YELLOW = "DARK_YELLOW"
    GRAY = "GRAY"
    DARK_GRAY = "DARK_GRAY"
    BLUE = "BLUE"
    GREEN = "GREEN"
    CYAN = "CYAN"
    RED = "RED"
    MAGENTA = "MAGENTA"
    YELLOW = "YELLOW"
    WHITE = "WHITE"


# Mapping from our Color enum to colorama colors
def _get_color_map() -> dict[Color, str]:
    """Build the color map based on colorama availability."""
    if not COLORAMA_AVAILABLE:
        return dict.fromkeys(Color, "")

    return {
        Color.BLACK: Fore.BLACK,
        Color.DARK_BLUE: Fore.BLUE,
        Color.DARK_GREEN: Fore.GREEN,
        Color.DARK_CYAN: Fore.CYAN,
        Color.DARK_RED: Fore.RED,
        Color.DARK_MAGENTA: Fore.MAGENTA,
        Color.DARK_YELLOW: Fore.YELLOW,
        Color.GRAY: Fore.WHITE,
        Color.DARK_GRAY: Fore.LIGHTBLACK_EX,
        Color.BLUE: Fore.LIGHTBLUE_EX,
        Color.GREEN: Fore.LIGHTGREEN_EX,
        Color.CYAN: Fore.LIGHTCYAN_EX,
        Color.RED: Fore.LIGHTRED_EX,
        Color.MAGENTA: Fore.LIGHTMAGENTA_EX,
        Color.YELLOW: Fore.LIGHTYELLOW_EX,
        Color.WHITE: Fore.LIGHTWHITE_EX,
    }


_COLOR_MAP = _get_color_map()


def init_colors() -> None:
    """
    Initialize colorama for cross-platform colored output.

    This function should be called once at the start of the application
    to enable colored output on Windows and other platforms.
    """
    if COLORAMA_AVAILABLE:
        colorama_init(autoreset=True)


def write_colored(text: str, color: Color | None = None, newline: bool = True) -> None:
    """
    Write colored text to the console.

    Args:
        text: The text to write
        color: The color to use (None for default)
        newline: Whether to add a newline at the end

    Example:
        >>> write_colored("Error!", Color.RED)
        >>> write_colored("Success!", Color.GREEN, newline=False)
    """
    if color and COLORAMA_AVAILABLE:
        color_code = _COLOR_MAP.get(color, "")
        output = f"{color_code}{text}{Style.RESET_ALL if COLORAMA_AVAILABLE else ''}"
    else:
        output = text

    if newline:
        print(output)
    else:
        print(output, end="")


def is_color_available() -> bool:
    """
    Check if colored output is available.

    Returns:
        True if colorama is installed and colors are available
    """
    return COLORAMA_AVAILABLE
