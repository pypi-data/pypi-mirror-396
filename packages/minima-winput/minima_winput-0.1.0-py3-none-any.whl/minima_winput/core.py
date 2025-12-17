"""
minima-winput core - Optimized Windows SendInput implementation.
Zero external dependencies. Minimal memory footprint.
"""

import ctypes
from ctypes import wintypes, sizeof, byref
from time import sleep

# === CONSTANTS (compile-time) ===
INPUT_KEYBOARD = 1
INPUT_MOUSE = 0

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE_ABS = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_SCANCODE_UP = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP

# Pre-computed mouse button flags
_MOUSE_DOWN = {'left': MOUSEEVENTF_LEFTDOWN, 'right': MOUSEEVENTF_RIGHTDOWN, 'middle': MOUSEEVENTF_MIDDLEDOWN}
_MOUSE_UP = {'left': MOUSEEVENTF_LEFTUP, 'right': MOUSEEVENTF_RIGHTUP, 'middle': MOUSEEVENTF_MIDDLEUP}

# Scan codes lookup
_SC = {
    'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12, 'f': 0x21,
    'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24, 'k': 0x25, 'l': 0x26,
    'm': 0x32, 'n': 0x31, 'o': 0x18, 'p': 0x19, 'q': 0x10, 'r': 0x13,
    's': 0x1F, 't': 0x14, 'u': 0x16, 'v': 0x2F, 'w': 0x11, 'x': 0x2D,
    'y': 0x15, 'z': 0x2C,
    '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06,
    '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
    'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E, 'f5': 0x3F,
    'f6': 0x40, 'f7': 0x41, 'f8': 0x42, 'f9': 0x43, 'f10': 0x44,
    'f11': 0x57, 'f12': 0x58,
    'esc': 0x01, 'tab': 0x0F, 'caps': 0x3A,
    'shift': 0x2A, 'lshift': 0x2A, 'rshift': 0x36,
    'ctrl': 0x1D, 'lctrl': 0x1D, 'rctrl': 0x9D,
    'alt': 0x38, 'lalt': 0x38, 'ralt': 0xB8,
    'space': 0x39, ' ': 0x39, 'enter': 0x1C,
    'backspace': 0x0E, 'delete': 0x53, 'insert': 0x52,
    'home': 0x47, 'end': 0x4F, 'pageup': 0x49, 'pagedown': 0x51,
    'up': 0x48, 'down': 0x50, 'left': 0x4B, 'right': 0x4D,
    '-': 0x0C, '=': 0x0D, '[': 0x1A, ']': 0x1B, '\\': 0x2B,
    ';': 0x27, "'": 0x28, '`': 0x29, ',': 0x33, '.': 0x34, '/': 0x35,
    'win': 0x5B, 'lwin': 0x5B, 'rwin': 0x5C,
}

# === STRUCTURES (minimal, packed) ===
class _KI(ctypes.Structure):
    __slots__ = ()
    _fields_ = [("vk", wintypes.WORD), ("sc", wintypes.WORD),
                ("fl", wintypes.DWORD), ("tm", wintypes.DWORD),
                ("ex", ctypes.POINTER(ctypes.c_ulong))]

class _MI(ctypes.Structure):
    __slots__ = ()
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("md", wintypes.DWORD), ("fl", wintypes.DWORD),
                ("tm", wintypes.DWORD), ("ex", ctypes.POINTER(ctypes.c_ulong))]

class _U(ctypes.Union):
    __slots__ = ()
    _fields_ = [("mi", _MI), ("ki", _KI)]

class _I(ctypes.Structure):
    __slots__ = ()
    _fields_ = [("tp", wintypes.DWORD), ("u", _U)]

# === PRE-ALLOCATED STRUCTURES (reused, zero allocation per call) ===
_ki = _I(tp=INPUT_KEYBOARD)
_mi = _I(tp=INPUT_MOUSE)
_ki2 = (_I * 2)(*((_I(tp=INPUT_KEYBOARD), _I(tp=INPUT_KEYBOARD))))
_INPUT_SIZE = sizeof(_I)

# === WINDOWS API ===
_u32 = ctypes.windll.user32
_SendInput = _u32.SendInput
_GetSystemMetrics = _u32.GetSystemMetrics
_MapVirtualKeyW = _u32.MapVirtualKeyW
_VkKeyScanW = _u32.VkKeyScanW

# === CACHED SCREEN SIZE ===
_screen_w = _GetSystemMetrics(0)
_screen_h = _GetSystemMetrics(1)
_scale_x = 65536.0 / _screen_w
_scale_y = 65536.0 / _screen_h

def _refresh_screen():
    """Call if screen resolution changes."""
    global _screen_w, _screen_h, _scale_x, _scale_y
    _screen_w = _GetSystemMetrics(0)
    _screen_h = _GetSystemMetrics(1)
    _scale_x = 65536.0 / _screen_w
    _scale_y = 65536.0 / _screen_h

def _sc(k):
    """Get scancode. Inline for hot path."""
    try:
        return _SC[k]
    except KeyError:
        return _SC.get(k.lower()) or _MapVirtualKeyW(_VkKeyScanW(ord(k)) & 0xFF, 0)

# === PUBLIC API ===

def key_down(k: str) -> None:
    """Press key down."""
    _ki.u.ki.sc = _sc(k)
    _ki.u.ki.fl = KEYEVENTF_SCANCODE
    _SendInput(1, byref(_ki), _INPUT_SIZE)

def key_up(k: str) -> None:
    """Release key."""
    _ki.u.ki.sc = _sc(k)
    _ki.u.ki.fl = KEYEVENTF_SCANCODE_UP
    _SendInput(1, byref(_ki), _INPUT_SIZE)

def key(k: str, duration: float = 0.0) -> None:
    """Press and release key. Single SendInput call when duration=0."""
    sc = _sc(k)
    if duration <= 0:
        _ki2[0].u.ki.sc = sc
        _ki2[0].u.ki.fl = KEYEVENTF_SCANCODE
        _ki2[1].u.ki.sc = sc
        _ki2[1].u.ki.fl = KEYEVENTF_SCANCODE_UP
        _SendInput(2, _ki2, _INPUT_SIZE)
    else:
        _ki.u.ki.sc = sc
        _ki.u.ki.fl = KEYEVENTF_SCANCODE
        _SendInput(1, byref(_ki), _INPUT_SIZE)
        sleep(duration)
        _ki.u.ki.fl = KEYEVENTF_SCANCODE_UP
        _SendInput(1, byref(_ki), _INPUT_SIZE)

def move(x: int, y: int) -> None:
    """Move mouse to absolute position."""
    _mi.u.mi.dx = int(x * _scale_x)
    _mi.u.mi.dy = int(y * _scale_y)
    _mi.u.mi.fl = MOUSEEVENTF_MOVE_ABS
    _SendInput(1, byref(_mi), _INPUT_SIZE)

def mouse_down(button: str = 'left') -> None:
    """Press mouse button."""
    _mi.u.mi.dx = 0
    _mi.u.mi.dy = 0
    _mi.u.mi.fl = _MOUSE_DOWN[button]
    _SendInput(1, byref(_mi), _INPUT_SIZE)

def mouse_up(button: str = 'left') -> None:
    """Release mouse button."""
    _mi.u.mi.dx = 0
    _mi.u.mi.dy = 0
    _mi.u.mi.fl = _MOUSE_UP[button]
    _SendInput(1, byref(_mi), _INPUT_SIZE)

def click(button: str, x: int, y: int) -> None:
    """Move and click."""
    dx = int(x * _scale_x)
    dy = int(y * _scale_y)
    _mi.u.mi.dx = dx
    _mi.u.mi.dy = dy
    _mi.u.mi.fl = MOUSEEVENTF_MOVE_ABS
    _SendInput(1, byref(_mi), _INPUT_SIZE)
    _mi.u.mi.fl = _MOUSE_DOWN[button]
    _SendInput(1, byref(_mi), _INPUT_SIZE)
    _mi.u.mi.fl = _MOUSE_UP[button]
    _SendInput(1, byref(_mi), _INPUT_SIZE)

def scroll(amount: int) -> None:
    """Scroll wheel. Positive=up, negative=down. 120=1 notch."""
    _mi.u.mi.dx = 0
    _mi.u.mi.dy = 0
    _mi.u.mi.md = amount
    _mi.u.mi.fl = MOUSEEVENTF_WHEEL
    _SendInput(1, byref(_mi), _INPUT_SIZE)
    _mi.u.mi.md = 0

def typewrite(text: str, interval: float = 0.0) -> None:
    """Type string. Optimized batch when interval=0."""
    if interval <= 0:
        for c in text:
            sc = _sc(c)
            _ki2[0].u.ki.sc = sc
            _ki2[0].u.ki.fl = KEYEVENTF_SCANCODE
            _ki2[1].u.ki.sc = sc
            _ki2[1].u.ki.fl = KEYEVENTF_SCANCODE_UP
            _SendInput(2, _ki2, _INPUT_SIZE)
    else:
        for c in text:
            key(c, 0)
            sleep(interval)

def hotkey(*keys) -> None:
    """Press key combination (e.g. hotkey('ctrl', 'c'))."""
    for k in keys:
        _ki.u.ki.sc = _sc(k)
        _ki.u.ki.fl = KEYEVENTF_SCANCODE
        _SendInput(1, byref(_ki), _INPUT_SIZE)
    for k in reversed(keys):
        _ki.u.ki.sc = _sc(k)
        _ki.u.ki.fl = KEYEVENTF_SCANCODE_UP
        _SendInput(1, byref(_ki), _INPUT_SIZE)
