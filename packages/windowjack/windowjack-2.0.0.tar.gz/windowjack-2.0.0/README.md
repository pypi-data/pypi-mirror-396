# WindowJack

A Python library for capturing windows and monitors on Windows, even when windows are occluded or hidden behind other windows.

## Installation

```bash
pip install windowjack
```

## Requirements

- Windows OS
- Python 3.7+
- numpy

## Features

- Capture entire monitors
- Capture specific windows by handle or title
- Capture occluded/hidden windows (windows behind other windows)
- Get list of all visible windows
- Get list of all monitors
- Region capture for monitors

## API Reference

### Functions

#### `list_windows()`
Returns a list of dictionaries containing information about all visible windows.

Each dictionary contains:
- `hwnd`: Window handle
- `title`: Window title
- `width`: Window width
- `height`: Window height

#### `list_monitors()`
Returns a list of dictionaries containing information about all monitors.

Each dictionary contains:
- `hmonitor`: Monitor handle
- `left`, `top`, `right`, `bottom`: Monitor coordinates
- `width`, `height`: Monitor dimensions
- `primary`: Boolean indicating if this is the primary monitor

### Classes

#### `WindowCapture(hwnd=None, title=None)`
Capture a specific window, even when occluded.

**Parameters:**
- `hwnd`: Window handle (int)
- `title`: Partial window title to search for (str)

**Methods:**
- `capture()`: Returns numpy array (RGB) of the window content
- `get_size()`: Returns (width, height) tuple
- `is_valid()`: Returns True if window still exists

**Properties:**
- `hwnd`: The window handle

#### `MonitorCapture(monitor_index=0)`
Capture an entire monitor.

**Parameters:**
- `monitor_index`: Index of the monitor (0 = primary)

**Methods:**
- `capture()`: Returns numpy array (RGB) of the entire monitor
- `capture_region(x, y, width, height)`: Capture a specific region
- `get_size()`: Returns (width, height) tuple

**Properties:**
- `monitor_info`: Dictionary with monitor information

## License

MIT License
