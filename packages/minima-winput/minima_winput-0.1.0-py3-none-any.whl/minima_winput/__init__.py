"""
minima-winput: Minimalist Windows input emulation library.
Uses Windows SendInput API with hardware scan codes for HID-like input.
"""

from .core import (
    key,
    key_down,
    key_up,
    click,
    mouse_down,
    mouse_up,
    move,
    scroll,
    typewrite,
    hotkey,
)

__version__ = "0.1.0"
__all__ = [
    "key",
    "key_down",
    "key_up",
    "click",
    "mouse_down",
    "mouse_up",
    "move",
    "scroll",
    "typewrite",
    "hotkey",
]
