import numpy as np
import win32gui
import mss

class WindowCapture:
    def __init__(self, window_name):
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Pencere bulunamadi: {}'.format(window_name))

    def _update_rect(self):
        client_origin = win32gui.ClientToScreen(self.hwnd, (0, 0))
        client_rect = win32gui.GetClientRect(self.hwnd)
        self.offset_x = client_origin[0]
        self.offset_y = client_origin[1]
        self.w = client_rect[2]
        self.h = client_rect[3]

    def get_screenshot(self):
        self._update_rect()
        monitor = {
            "left": self.offset_x,
            "top": self.offset_y,
            "width": self.w,
            "height": self.h
        }
        with mss.mss() as sct:
            img = sct.grab(monitor)
            frame = np.array(img)[..., :3]
            return np.ascontiguousarray(frame)

    def get_screen_position(self, pos):
        self._update_rect()
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)