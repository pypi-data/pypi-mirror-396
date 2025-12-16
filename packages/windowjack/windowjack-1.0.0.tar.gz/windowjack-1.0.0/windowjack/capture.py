import ctypes
from ctypes import wintypes
import numpy as np
from typing import Optional, List, Tuple, Dict

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
dwmapi = ctypes.windll.dwmapi
shcore = ctypes.windll.shcore

SRCCOPY = 0x00CC0020
CAPTUREBLT = 0x40000000
DIB_RGB_COLORS = 0
BI_RGB = 0
PW_RENDERFULLCONTENT = 0x00000002
DWMWA_EXTENDED_FRAME_BOUNDS = 9


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", wintypes.DWORD * 3),
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


def list_windows() -> List[Dict]:
    windows = []
    
    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def enum_callback(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                if width > 0 and height > 0:
                    windows.append({
                        "hwnd": hwnd,
                        "title": buffer.value,
                        "width": width,
                        "height": height,
                    })
        return True
    
    user32.EnumWindows(enum_callback, 0)
    return windows


def list_monitors() -> List[Dict]:
    monitors = []
    
    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
    def enum_callback(hmonitor, hdc, lprect, lparam):
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        user32.GetMonitorInfoW(hmonitor, ctypes.byref(info))
        rect = info.rcMonitor
        monitors.append({
            "hmonitor": hmonitor,
            "left": rect.left,
            "top": rect.top,
            "right": rect.right,
            "bottom": rect.bottom,
            "width": rect.right - rect.left,
            "height": rect.bottom - rect.top,
            "primary": bool(info.dwFlags & 1),
        })
        return True
    
    user32.EnumDisplayMonitors(None, None, enum_callback, 0)
    return monitors


def _capture_to_numpy(hdc_src, x: int, y: int, width: int, height: int) -> np.ndarray:
    hdc_mem = gdi32.CreateCompatibleDC(hdc_src)
    hbm = gdi32.CreateCompatibleBitmap(hdc_src, width, height)
    gdi32.SelectObject(hdc_mem, hbm)
    
    gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc_src, x, y, SRCCOPY | CAPTUREBLT)
    
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB
    
    buffer = ctypes.create_string_buffer(width * height * 4)
    gdi32.GetDIBits(hdc_mem, hbm, 0, height, buffer, ctypes.byref(bmi), DIB_RGB_COLORS)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    
    img = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)
    return img[:, :, :3][:, :, ::-1].copy()


def _capture_window_printwindow(hwnd: int, width: int, height: int) -> np.ndarray:
    hdc_window = user32.GetDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_window)
    hbm = gdi32.CreateCompatibleBitmap(hdc_window, width, height)
    gdi32.SelectObject(hdc_mem, hbm)
    
    user32.PrintWindow(hwnd, hdc_mem, PW_RENDERFULLCONTENT)
    
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB
    
    buffer = ctypes.create_string_buffer(width * height * 4)
    gdi32.GetDIBits(hdc_mem, hbm, 0, height, buffer, ctypes.byref(bmi), DIB_RGB_COLORS)
    
    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(hwnd, hdc_window)
    
    img = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)
    return img[:, :, :3][:, :, ::-1].copy()


class WindowCapture:
    def __init__(self, hwnd: Optional[int] = None, title: Optional[str] = None):
        self._hwnd = None
        if hwnd is not None:
            self._hwnd = hwnd
        elif title is not None:
            windows = list_windows()
            for w in windows:
                if title.lower() in w["title"].lower():
                    self._hwnd = w["hwnd"]
                    break
            if self._hwnd is None:
                raise ValueError(f"Window with title containing '{title}' not found")
        else:
            raise ValueError("Either hwnd or title must be provided")
    
    @property
    def hwnd(self) -> int:
        return self._hwnd
    
    def get_size(self) -> Tuple[int, int]:
        rect = wintypes.RECT()
        dwmapi.DwmGetWindowAttribute(
            self._hwnd,
            DWMWA_EXTENDED_FRAME_BOUNDS,
            ctypes.byref(rect),
            ctypes.sizeof(rect)
        )
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        if width <= 0 or height <= 0:
            user32.GetWindowRect(self._hwnd, ctypes.byref(rect))
            width = rect.right - rect.left
            height = rect.bottom - rect.top
        return width, height
    
    def capture(self) -> np.ndarray:
        width, height = self.get_size()
        return _capture_window_printwindow(self._hwnd, width, height)
    
    def is_valid(self) -> bool:
        return bool(user32.IsWindow(self._hwnd))


class MonitorCapture:
    def __init__(self, monitor_index: int = 0):
        monitors = list_monitors()
        if monitor_index < 0 or monitor_index >= len(monitors):
            raise ValueError(f"Monitor index {monitor_index} out of range (0-{len(monitors)-1})")
        self._monitor = monitors[monitor_index]
        self._index = monitor_index
    
    @property
    def monitor_info(self) -> Dict:
        return self._monitor.copy()
    
    def get_size(self) -> Tuple[int, int]:
        return self._monitor["width"], self._monitor["height"]
    
    def capture(self) -> np.ndarray:
        hdc_screen = user32.GetDC(None)
        left = self._monitor["left"]
        top = self._monitor["top"]
        width = self._monitor["width"]
        height = self._monitor["height"]
        
        result = _capture_to_numpy(hdc_screen, left, top, width, height)
        user32.ReleaseDC(None, hdc_screen)
        return result
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        hdc_screen = user32.GetDC(None)
        abs_x = self._monitor["left"] + x
        abs_y = self._monitor["top"] + y
        
        result = _capture_to_numpy(hdc_screen, abs_x, abs_y, width, height)
        user32.ReleaseDC(None, hdc_screen)
        return result
