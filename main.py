from windowcapture import WindowCapture
import cv2 as cv
import numpy as np
import os
import win32api, win32con, win32gui
import time
from math import sqrt
import ctypes
from ctypes import wintypes
from pynput import keyboard as pynkeyboard
from pynput.keyboard import Controller as KeyboardController
import random

running = True
paused = False
kb = KeyboardController()

def on_press(key):
    global running, paused
    try:
        if key == pynkeyboard.Key.end:
            running = False
            print("[CIKIS]")
        elif key == pynkeyboard.Key.f12:
            paused = not paused
            print("[DURAKLAT]" if paused else "[DEVAM]")
    except:
        pass

listener = pynkeyboard.Listener(on_press=on_press)
listener.daemon = True
listener.start()

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long), ("dy", ctypes.c_long),
        ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _anonymous_ = ("_input",)
    _fields_ = [("type", wintypes.DWORD), ("_input", _INPUT)]

def send_click(x, y):
    screen_w = win32api.GetSystemMetrics(0)
    screen_h = win32api.GetSystemMetrics(1)
    x, y = int(x), int(y)
    if x < 0 or y < 0 or x >= screen_w or y >= screen_h:
        return
    abs_x = int(x * 65535 / screen_w)
    abs_y = int(y * 65535 / screen_h)
    for flags in [
        win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE,
        win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_ABSOLUTE,
        win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_ABSOLUTE
    ]:
        inp = INPUT(type=0)
        inp.mi.dx = abs_x
        inp.mi.dy = abs_y
        inp.mi.dwFlags = flags
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        time.sleep(0.08)

def press_key(key, duration):
    kb.press(key)
    time.sleep(duration)
    kb.release(key)

def rotate_camera():
    screen_w = win32api.GetSystemMetrics(0)
    screen_h = win32api.GetSystemMetrics(1)
    cx, cy = screen_w // 2, screen_h // 2
    ctypes.windll.user32.SetCursorPos(cx, cy)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
    time.sleep(0.05)
    turn = random.choice([-350, -250, 250, 350])
    for _ in range(20):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, turn // 20, 0)
        time.sleep(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
    time.sleep(0.1)

def wander():
    print("[GEZME] Tas yok, etraf taraniyor...")
    rotate_camera()
    time.sleep(0.3)
    direction = random.choice(['w', 'w', 'w', 'a', 'd', 's'])
    duration = random.uniform(1.5, 3.0)
    print(f"[GEZME] '{direction}' yonunde {duration:.1f}sn")
    press_key(direction, duration)
    time.sleep(0.3)
    rotate_camera()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TOP_SKIP = 100
BOTTOM_SKIP = 80
CLICK_OFFSET_Y = 60

# Sadece gercekci boyutlar - yazı buyuk degismez, kamera zoom degisir
SCALES = [0.7, 0.85, 1.0, 1.15, 1.3]
THRESHOLD = 0.50

def euqli_dist(p, q):
    return sqrt(((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2))

def closest(cur_pos, positions):
    low_dist = float('inf')
    closest_pos = None
    for pos in positions:
        dist = euqli_dist(cur_pos, pos)
        if dist < low_dist:
            low_dist = dist
            closest_pos = pos
    return closest_pos

def findStonePositions(needle_img_path, haystack_img, threshold):
    needle_orig = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
    if needle_orig is None:
        return []
    if len(needle_orig.shape) == 3 and needle_orig.shape[2] == 4:
        needle_orig = cv.cvtColor(needle_orig, cv.COLOR_BGRA2BGR)

    h_img = haystack_img.shape[0]
    search_area = haystack_img[TOP_SKIP: h_img - BOTTOM_SKIP, :]

    best_points = []
    best_score = 0

    for scale in SCALES:
        needle = cv.resize(needle_orig, None, fx=scale, fy=scale)
        needle_w = needle.shape[1]
        needle_h = needle.shape[0]

        if needle_w >= search_area.shape[1] or needle_h >= search_area.shape[0]:
            continue

        result = cv.matchTemplate(search_area, needle, cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(result)

        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))

        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
            rectangles.append(rect)
            rectangles.append(rect)

        if len(rectangles):
            rectangles, _ = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
            points = []
            for (x, y, w, h) in rectangles:
                cx = x + int(w / 2)
                real_y = y + TOP_SKIP
                cy = real_y + h + CLICK_OFFSET_Y
                points.append((cx, cy))

            # En iyi skoru veren scale'i kullan
            if max_val > best_score and points:
                best_score = max_val
                best_points = points

    return best_points

def findCharPositions(needle_img_path, haystack_img, threshold):
    needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
    if needle_img is None:
        return []
    if len(needle_img.shape) == 3 and needle_img.shape[2] == 4:
        needle_img = cv.cvtColor(needle_img, cv.COLOR_BGRA2BGR)
    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]
    result = cv.matchTemplate(haystack_img, needle_img, cv.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))
    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
        rectangles.append(rect)
        rectangles.append(rect)
    points = []
    if len(rectangles):
        rectangles, _ = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        for (x, y, w, h) in rectangles:
            points.append((x + int(w/2), y + int(h/2)))
    return points

def tryAllHeaders():
    with open("headers.txt", "r") as f:
        headers = [h.strip() for h in f if h.strip()]
    for header in headers:
        try:
            wincap = WindowCapture(header)
            print(f"[OK] Pencere: {header}")
            return header
        except:
            continue
    print("[HATA] Pencere bulunamadi!")
    return None

def getStoneList():
    with open("stones.txt", "r") as f:
        return [s.strip() for s in f if s.strip()]

def Start():
    global running, paused
    char = "char.jpg"
    playerTreshold = 0.5
    i = 0
    playerLocation = []
    locked_target = None
    locked_miss_count = 0
    MAX_MISS = 8
    no_stone_count = 0
    WANDER_AFTER = 6

    print("=== BOT BASLADI ===")
    print("F12 = Duraklat/Devam | END = Cik")

    header = tryAllHeaders()
    if header is None:
        return
    wincap = WindowCapture(header)
    stones = getStoneList()
    print(f"[INFO] Aranacak: {stones} | Threshold: {THRESHOLD}")
    print("[HAZIR] Oyuna gec")

    while running:
        if paused:
            time.sleep(0.1)
            continue

        try:
            screen = wincap.get_screenshot()

            StonePoints = []
            for stone in stones:
                pts = findStonePositions(stone, screen, THRESHOLD)
                if pts:
                    StonePoints = pts
                    break

            if i % 10 == 0 or len(playerLocation) == 0:
                playerLocation = findCharPositions(char, screen, playerTreshold)

            if len(StonePoints) > 0:
                no_stone_count = 0
                locked_miss_count = 0

                if len(playerLocation) > 0:
                    closestStone = closest(playerLocation[0], StonePoints)
                else:
                    closestStone = StonePoints[0]

                sx, sy = wincap.get_screen_position(closestStone)
                sx, sy = int(sx), int(sy)
                locked_target = (sx, sy)

                if i % 15 == 0:
                    print(f"[TIKLA] ({sx}, {sy}) | Tas:{len(StonePoints)}")

                send_click(sx, sy)

            elif locked_target is not None:
                locked_miss_count += 1
                if locked_miss_count <= MAX_MISS:
                    if locked_miss_count == 1:
                        print("[KILITLI] Vurmaya devam...")
                    send_click(locked_target[0], locked_target[1])
                else:
                    print("[YENİ TAS] Tas oldu, yeni tas aranıyor...")
                    locked_target = None
                    locked_miss_count = 0
                    no_stone_count = 0
                    time.sleep(0.5)

            else:
                no_stone_count += 1
                if no_stone_count >= WANDER_AFTER:
                    wander()
                    no_stone_count = 0
                else:
                    time.sleep(0.3)

            i += 1
            time.sleep(0.4)

        except Exception as e:
            print(f"[HATA] {e}")
            i += 1
            time.sleep(0.3)

    print("=== BOT KAPATILDI ===")

Start()