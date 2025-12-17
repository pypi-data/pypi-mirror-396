# minima-winput

Minimalist Windows input emulation library. Zero dependencies. Maximum performance.

## Overview

- **What**: Python library for keyboard and mouse input emulation on Windows
- **How**: Uses Windows `SendInput` API with hardware scan codes via `ctypes`
- **Why**: HID-like input at system level, not window-specific messages
- **Performance**: ~350,000 key presses per second, ~2.8μs per call

## Installation

```bash
# From local directory
pip install -e ./winput

# Or copy minima_winput folder to your project
```

## Quick Start

```python
from minima_winput import key, click, move, typewrite, hotkey

key('w')                     # Press and release W
click('left', 500, 300)      # Left click at coordinates
move(100, 200)               # Move mouse cursor
typewrite('hello')           # Type string
hotkey('ctrl', 'c')          # Key combination
```

---

## API Reference

### Keyboard Functions

#### `key(k: str, duration: float = 0.0) -> None`
Press and release a key.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| k | str | required | Key to press |
| duration | float | 0.0 | Hold time in seconds. When 0, uses single optimized SendInput call |

```python
key('w')           # Press W (instant)
key('space')       # Press spacebar
key('enter')       # Press enter
key('a', 0.1)      # Hold A for 100ms
```

#### `key_down(k: str) -> None`
Press and hold a key without releasing.

```python
key_down('shift')  # Hold shift
key('a')           # Types 'A' (uppercase)
key_up('shift')    # Release shift
```

#### `key_up(k: str) -> None`
Release a held key.

```python
key_up('shift')
key_up('ctrl')
```

#### `typewrite(text: str, interval: float = 0.0) -> None`
Type a string of characters.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| text | str | required | String to type |
| interval | float | 0.0 | Delay between characters in seconds |

```python
typewrite('Hello World')        # Type instantly
typewrite('Hello', 0.05)        # Type with 50ms delay between chars
```

#### `hotkey(*keys) -> None`
Press multiple keys simultaneously (key combination).

```python
hotkey('ctrl', 'c')             # Copy
hotkey('ctrl', 'v')             # Paste
hotkey('ctrl', 'shift', 'esc')  # Task Manager
hotkey('alt', 'f4')             # Close window
hotkey('win', 'd')              # Show desktop
```

---

### Mouse Functions

#### `move(x: int, y: int) -> None`
Move mouse cursor to absolute screen position.

| Parameter | Type | Description |
|-----------|------|-------------|
| x | int | X coordinate (pixels from left) |
| y | int | Y coordinate (pixels from top) |

```python
move(0, 0)         # Top-left corner
move(500, 300)     # Center area
move(1920, 1080)   # Bottom-right (on 1080p screen)
```

#### `click(button: str, x: int, y: int) -> None`
Move to position and click.

| Parameter | Type | Description |
|-----------|------|-------------|
| button | str | 'left', 'right', or 'middle' |
| x | int | X coordinate |
| y | int | Y coordinate |

```python
click('left', 500, 300)    # Left click
click('right', 500, 300)   # Right click (context menu)
click('middle', 500, 300)  # Middle click
```

#### `mouse_down(button: str = 'left') -> None`
Press mouse button without releasing.

```python
mouse_down('left')         # Start drag
move(600, 400)             # Drag to position
mouse_up('left')           # End drag
```

#### `mouse_up(button: str = 'left') -> None`
Release mouse button.

```python
mouse_up('left')
mouse_up('right')
```

#### `scroll(amount: int) -> None`
Scroll mouse wheel.

| Parameter | Type | Description |
|-----------|------|-------------|
| amount | int | Scroll amount. Positive = up, negative = down. 120 = 1 notch |

```python
scroll(120)        # Scroll up 1 notch
scroll(-120)       # Scroll down 1 notch
scroll(360)        # Scroll up 3 notches
scroll(-600)       # Scroll down 5 notches
```

---

## Supported Keys

### Letters
`a` `b` `c` `d` `e` `f` `g` `h` `i` `j` `k` `l` `m` `n` `o` `p` `q` `r` `s` `t` `u` `v` `w` `x` `y` `z`

### Numbers
`0` `1` `2` `3` `4` `5` `6` `7` `8` `9`

### Function Keys
`f1` `f2` `f3` `f4` `f5` `f6` `f7` `f8` `f9` `f10` `f11` `f12`

### Modifiers
| Key | Aliases |
|-----|---------|
| Left Shift | `shift`, `lshift` |
| Right Shift | `rshift` |
| Left Ctrl | `ctrl`, `lctrl` |
| Right Ctrl | `rctrl` |
| Left Alt | `alt`, `lalt` |
| Right Alt | `ralt` |
| Windows | `win`, `lwin` |
| Right Windows | `rwin` |

### Special Keys
| Key | Aliases |
|-----|---------|
| Space | `space`, ` ` |
| Enter | `enter` |
| Backspace | `backspace` |
| Tab | `tab` |
| Escape | `esc` |
| Caps Lock | `caps` |
| Delete | `delete` |
| Insert | `insert` |

### Navigation
`up` `down` `left` `right` `home` `end` `pageup` `pagedown`

### Punctuation
`` ` `` `-` `=` `[` `]` `\` `;` `'` `,` `.` `/`

---

## Technical Details

### How It Works

1. **Windows API**: Uses `SendInput` from `user32.dll` via Python `ctypes`
2. **Scan Codes**: Uses hardware scan codes (`KEYEVENTF_SCANCODE`) instead of virtual key codes
3. **System Level**: Injects input into the system input stream, not specific windows

### Why Scan Codes?

Virtual Key codes are Windows abstractions. Scan codes are the actual codes sent by keyboard hardware. Using scan codes:
- More closely emulates real hardware
- Works with applications that read raw input
- Bypasses some input filtering

### Performance Optimizations

| Optimization | Description |
|--------------|-------------|
| Pre-allocated structures | INPUT structures created once at module load, reused for all calls |
| Cached screen metrics | Screen size cached, not queried per call |
| Batched SendInput | `key()` with duration=0 sends press+release in single API call |
| Direct API binding | `_SendInput = user32.SendInput` avoids attribute lookup |
| `__slots__` | Reduces memory footprint of ctypes structures |

### Memory Usage

- Static allocation: ~264 bytes for pre-allocated INPUT structures
- Zero allocation per call (structures are reused)

### Benchmark

```
key()  x1000: 2.82ms  (2.8μs per call)  ~357,000 calls/sec
move() x1000: 32.48ms (32.5μs per call) ~30,800 calls/sec
```

---

## Examples

### Hold key for duration
```python
from minima_winput import key_down, key_up
from time import sleep

key_down('w')
sleep(2.0)        # Hold W for 2 seconds
key_up('w')
```

### Drag and drop
```python
from minima_winput import move, mouse_down, mouse_up
from time import sleep

move(100, 100)           # Start position
mouse_down('left')
sleep(0.1)
move(500, 500)           # End position
mouse_up('left')
```

### Game input (WASD)
```python
from minima_winput import key_down, key_up
from time import sleep

# Move forward-right for 1 second
key_down('w')
key_down('d')
sleep(1.0)
key_up('w')
key_up('d')
```

### Text input with modifiers
```python
from minima_winput import key_down, key_up, typewrite, key

# Type "Hello" then SHIFT+1 for "!"
typewrite('Hello')
key_down('shift')
key('1')           # Types "!"
key_up('shift')
```

### Keyboard shortcuts
```python
from minima_winput import hotkey

hotkey('ctrl', 'a')      # Select all
hotkey('ctrl', 'c')      # Copy
hotkey('alt', 'tab')     # Switch window
hotkey('ctrl', 'v')      # Paste
```

---

## Limitations

- **Windows only**: Uses Windows-specific APIs
- **No Unicode**: Scan codes don't support Unicode characters directly
- **Admin apps**: May not work with elevated/admin applications from non-admin process
- **Anti-cheat**: Some games block SendInput

## License

MIT
