import sys
import os
import math
import random
import datetime
import psutil
import calendar
from services.weather_service import WeatherService
from config import LATITUDE, LONGITUDE, LOCATION_NAME
from services.system_service import SystemService
from core.state import JarvisState
from addons.voice_controller import VoiceController

from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from services.handtracking_service import HandTrackingService
from services.settings_service import SettingsService
from PySide6.QtGui import QPolygon
from PySide6.QtCore import QPoint

class HUDOverlay(QWidget):
    """
    Main ATLAS window

    This class draws everything that appears on top of the map, including the orb,
    panels, boot screen, scan overlay, hand tracking display, and vision

    FEATURES:
        1. Main orb
        2. Boot Screen
        3. Weather and System panels
        4. Scan
        5. Music panel
        6. Hand Landmark
        7. Target Boxes
    ARGS:
        state: ATLAS state manager
        gesture: Hand tracking service
        vision: Vision service
    """
    def __init__(self, state, gesture, vision):
        super().__init__()

        self.t = 0
        self.angle = 0
        self.base_radius = 68
        self.state_manager = state
        self.gesture = gesture
        self.state = "STANDBY"
        self.particles = []
        self.vision = vision
        for _ in range(70):
            self.particles.append({"angle": random.uniform(0, math.tau), "distance": random.uniform(120, 230), "speed": random.uniform(0.15, 0.7), "size": random.randint(1, 3)})

        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
        self.weather_service = WeatherService(LATITUDE, LONGITUDE, LOCATION_NAME)
        self.system_service = SystemService()
        self.system_stats = self.system_service.get_stats()
        self.system_timer = 0
        self.booting = True
        self.start_boot = datetime.datetime.now().timestamp()
        self.boot_time = 23.0
        self.boot_voice_stage = -1

    def animate(self):
        """
        Updates the HUD animations

        Runs every frame and updates
        animation time, orb rotation,
        and system stats
        """

        #Update the animation values
        self.t += 0.016
        self.angle += 0.016 * 0.9

        #Refresh the stats every second
        self.system_timer += 0.016
        if self.system_timer >= 1.0:
            self.system_stats = self.system_service.get_stats()
            self.system_timer = 0

        #Redraw
        self.update()

    def draw_system_panel(self, painter):
        w = self.width()
        h = self.height()

        x = w - 330
        y = h - 170

        self.draw_panel(painter, x, y, 280, 120, "System")

        painter.setFont(QFont("Courier New", 22))
        painter.setPen(QColor(150, 235, 255, 230))

        painter.drawText(x + 25, y + 65, f"CPU  {self.system_stats['cpu']}%")
        painter.drawText(x + 25, y + 90, f"RAM  {self.system_stats['ram']}%")
        painter.drawText(x + 25, y + 115, f"BAT  {self.system_stats['battery']}%")

    def draw_panel(self, painter, x, y, w, h, title):
        painter.setPen(QPen(QColor(0, 210, 255, 130), 1))
        painter.setBrush(QColor(0, 25, 35, 120))
        painter.drawRoundedRect(x, y, w, h, 12, 12)

        painter.setFont(QFont("Courier New", 14))
        painter.setPen(QColor(150, 235, 255, 230))
        painter.drawText(x, y + 10, w, 20, Qt.AlignCenter, title.upper())

        painter.setPen(QPen(QColor(0, 210, 255, 120), 1))
        painter.drawLine(x + 15, y + 34, x + w - 15, y + 34)

    def draw_time_panel(self, painter):
        w, h = self.width(), self.height()
        x = w - 330
        y = 45

        self.draw_panel(painter, x, y, 280, 110, "TIME")

        now = datetime.datetime.now()
        time_text = now.strftime("%I:%M:%S %p")
        date_text = now.strftime("%A, %b %d")

        painter.setFont(QFont("Courier New", 28))
        painter.setPen(QColor(150, 235, 255, 230))
        painter.drawText(x + 20, y + 70, time_text)

        painter.setFont(QFont("Courier New", 18))
        painter.setPen(QColor(0, 130, 180, 220))
        painter.drawText(x + 22, y + 100, date_text)

    def draw_weather_panel(self, painter):
        h = self.height()
        x = 50
        y = h - 190

        self.draw_panel(painter, x, y, 390, 150, "Weather")

        weather = self.weather_service.get_weather()

        painter.setFont(QFont("Courier New", 14))
        painter.setPen(QColor(150, 235, 255, 230))
        painter.drawText(x + 22, y + 55, weather["location"])

        painter.setFont(QFont("Courier New", 28))
        painter.drawText(x + 22, y + 92, f'{weather["temperature"]}°F')

        painter.setFont(QFont("Courier New", 18))
        painter.setPen(QColor(0, 130, 180, 220))
        painter.drawText(x + 22, y + 125, f'Precipitation: {weather["precipitation"]}')

        painter.setFont(QFont("Courier New", 14))
        painter.drawText(x + 22, y + 148, f'Wind: {weather["wind"]} mph')

    def paintEvent(self, event):
        """
        Draws the full ATLAS interface

        This is the main drawing method.
        It decides whether to show the boot screen
        or the normal ATLAS HUD
        """

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        #Gets the current ATLAS state
        self.state = self.state_manager.get()
        focus = (self.state == "FOCUS")

        #Show the boot screen first
        if self.booting:
            parent = self.parent()

            if hasattr(parent, "face_v"):
                parent.face_v.show()
                parent.face_v.raise_()

            self.draw_boot_sequence(painter)

            time_now = datetime.datetime.now().timestamp()

            if time_now - self.start_boot >= self.boot_time:
                self.booting = False

                if hasattr(parent, "face_v"):
                    parent.face_v.hide()

            return

        #Draw the main HUD after boot finishes
        self.draw_main_status_bar(painter, w, h)


        # bottom right
        cx = w - 185
        cy = h - 455

        pulse = math.sin(self.t * 2.5) * 8
        radius = self.base_radius + pulse - 10

        self.draw_scan_overlay(painter)
        self.draw_target_overlay(painter)
        self.draw_screen_boxes(painter)
        self.draw_particles(painter, cx, cy)
        self.draw_glow(painter, cx, cy, radius)
        self.draw_core(painter, cx, cy, radius)
        self.draw_rings(painter, cx, cy, radius)
        self.draw_voice_waveform(painter, cx, cy, radius)
        self.draw_state_text(painter, cx, cy)
        self.draw_time_panel(painter)

        #Hide any extra panels during focus mode
        if not focus:
            self.draw_weather_panel(painter)
            self.draw_system_panel(painter)
            self.draw_calendar_panel(painter)
            self.draw_music_panel(painter)
            self.draw_hand_landmarks(painter)

    def draw_screen_boxes(self, painter):
        boxes = self.state_manager.get_screen_boxes()

        if not boxes:
            return

        painter.setFont(QFont("Courier New",10))

        for box in boxes:
            x = box["x"]
            y = box["y"]
            w = box["w"]
            h = box["h"]

            glow = QColor(255,60,60,180)

            painter.setPen(QPen(glow,3))

            painter.drawRoundedRect(x - 8, y - 8, w + 16, h + 16, 8, 8)

            painter.setPen(QColor(255, 180, 180))

            painter.drawText(x, y - 12, "ERROR DETECTED")

    def draw_main_status_bar(self, painter, w, h):
        parent = self.parent()
        mode = getattr(parent, "current_mode", "MAP")
        if parent.gesture is None:
            stat = "GESTURE OFF"
        else:
            stat = "GESTURE ON"

        if self.vision.running:
            vision_status = "VISION ON"
        else:
            vision_status = "VISION OFF"

        state = self.state_manager.get()

        x = w // 2 - 330
        y = 22
        bw = 720
        bh = 42
        cyan = QColor(0, 220, 255, 190)
        d = QColor(0, 120, 170, 120)
        bright = QColor(160, 245, 255, 230)

        painter.setBrush(QColor(0, 20, 32, 135))
        painter.setPen(QPen(cyan, 1))
        painter.drawRoundedRect(x, y, bw, bh, 10, 10)

        painter.setPen(QPen(d, 1))
        painter.drawLine(x+16, y+bh-9, x+bw-18, y+bh-9)

        painter.setFont(QFont("Courier New", 13))
        painter.setPen(bright)

        t = f"ATLAS ACTIVE  |  {mode} MODE  |  {state}  |  {stat}  |  {vision_status}"

        painter.drawText(x, y + 18, bw, 20, Qt.AlignCenter, t)


    def draw_boot_sequence(self, painter):
        """
        Draws the ATLAS startup screen

        Shows the boot animation, loading steps,
        user recognition panel, weather preview,
        and progress bar
        """

        w = self.width()
        h = self.height()

        time_now = datetime.datetime.now().timestamp()

        passed_time = time_now - self.start_boot

        #Calculate boot progress
        loading = min(1.0, passed_time / self.boot_time)

        c1 = w // 2
        c2 = h // 2 + 20

        #Draw dark background
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 245))

        cyan_color = QColor(0, 220, 255, 230)
        bright = QColor(150, 245, 255, 245)

        painter.setFont(QFont("Courier New", 34))
        painter.setPen(bright)

        painter.drawText(0, 55, w, 55, Qt.AlignCenter, "A.T.L.A.S")

        #Draw the orb
        painter.setFont(QFont("Courier New", 18))
        painter.setPen(cyan_color)

        painter.drawText(0, 150, w, 35, Qt.AlignCenter, "SYSTEM INITIALIZING")

        # orb
        orb_pulse = math.sin(passed_time * 4) * 7

        r = 78 + orb_pulse

        painter.setPen(Qt.NoPen)

        for i in range(18, 0, -1):
            r2 = r + i * 10

            a = max(3, 34 - i)

            painter.setBrush(QColor(0, 190, 255, a))

            painter.drawEllipse(int(c1 - r2), int(c2 - r2), int(r2 * 2), int(r2 * 2))

        painter.setBrush(QColor(0, 45, 70, 180))

        painter.setPen(QPen(QColor(0, 230, 255, 245), 2))

        painter.drawEllipse(int(c1 - r), int(c2 - r), int(r * 2), int(r * 2))

        # inner lines
        painter.setPen(QPen(QColor(120, 245, 255, 80), 1))

        for i in range(16):
            a_x = passed_time * 0.6 + i * math.tau / 16

            x1 = c1 + math.cos(a_x) * r * 0.15
            y1 = c2 + math.sin(a_x) * r * 0.15

            x2 = c1 + math.cos(a_x * 1.7) * r * 0.75
            y2 = c2 + math.sin(a_x * 1.7) * r * 0.75

            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # core
        for i in range(6, 0, -1):
            r1 = r * (0.12 + i * 0.08)

            painter.setBrush(QColor(0, 220, 255, 18 + i * 8))

            painter.setPen(QPen(QColor(130, 250, 255, 70 + i * 18),1))

            painter.drawEllipse(int(c1 - r1),int(c2 - r1),int(r1 * 2),int(r1 * 2))

        # rings
        painter.setBrush(Qt.NoBrush)

        for rings in range(5):

            r3 = r + 25 + rings * 18

            if rings % 2 == 0:
                painter.setPen(QPen(QColor(0, 220, 255, 150), 2))
            else:
                painter.setPen(QPen(QColor(0, 220, 255, 150), 1))

            for j in range(6):
                start = int((passed_time * (90 + rings * 12)+ j * 60+ rings * 30) * 16)

                s_p = int((22 + rings * 3) * 16)

                painter.drawArc(int(c1 - r3), int(c2 - r3), int(r3 * 2), int(r3 * 2), start, s_p)

        # steps
        steps = [
            "LOADING MAP",
            "LOADING VOICE CONTROLS",
            "LOADING MOTION SENSORS",
            "CONNECTING AI SYSTEMS",
            "SYSTEM ONLINE"
        ]

        b_x = 65
        b_y = h // 2 - 100

        b_w = 420
        b_h = 62

        gap = 24

        #Draw loading steps
        for i, step in enumerate(steps):

            y = b_y + i * (b_h + gap)

            act = loading * len(steps) >= i + 1

            if act:
                color = QColor(0, 245, 255, 235)
                status = "ONLINE"
            else:
                color = QColor(0, 110, 150, 170)
                status = "WAIT"

            painter.setBrush(QColor(0, 25, 38, 180))

            painter.setPen(QPen(color, 1))

            painter.drawRoundedRect(b_x, y, b_w, b_h, 8, 8)

            painter.drawLine(b_x + b_w, y + b_h // 2, c1 - r - 80, y + b_h // 2)

            painter.drawEllipse(c1 - r - 88, y + b_h // 2 - 5, 10, 10)

            painter.setFont(QFont("Courier New", 16))

            painter.drawText(b_x + 20, y + 38, f"{i + 1:02}")

            painter.setFont(QFont("Courier New", 12))

            painter.drawText(b_x + 82, y + 25, step)

            painter.drawText(b_x + 82, y + 48, f"STATUS: {status}")

        # 3D face frame
        panel_x = w - 450
        panel_y = h // 2 - 315
        panel_y = h // 2 - 250

        panel_w = 450
        panel_h = 620

        painter.setBrush(QColor(0, 20, 32, 95))

        painter.setPen(QPen(cyan_color, 1))

        painter.drawRoundedRect(panel_x, panel_y, panel_w, panel_h, 10, 10)

        painter.setFont(QFont("Courier New", 15))

        painter.setPen(cyan_color)

        painter.drawText(panel_x, panel_y - 28, panel_w, 25, Qt.AlignCenter, "USER RECOGNITION")

        painter.setFont(QFont("Courier New", 13))

        painter.setPen(bright)

        painter.drawText(panel_x + 30, panel_y + panel_h - 85, "SCAN STATUS: SCANNING...")

        painter.drawText(panel_x + 30, panel_y + panel_h - 55, "IDENTITY: RECOGNIZING")

        painter.drawText(panel_x + 30, panel_y + panel_h - 25, f"CONFIDENCE: {int(loading * 100)}%")

        # progress bar
        ba_w = 520
        ba_h = 18

        ba_x = (w - ba_w) // 2
        ba_y = h - 155

        painter.setFont(QFont("Courier New", 15))

        painter.setPen(cyan_color)

        painter.drawText(0, ba_y - 35, w, 30, Qt.AlignCenter, "PROGRESS")

        painter.setBrush(QColor(0, 20, 30, 190))

        painter.setPen(QPen(cyan_color, 1))

        painter.drawRoundedRect(ba_x, ba_y, ba_w, ba_h, 6, 6)

        painter.setBrush(QColor(0, 220, 255, 210))

        painter.setPen(Qt.NoPen)

        painter.drawRoundedRect(ba_x + 2, ba_y + 2, int((ba_w - 4) * loading), ba_h - 4, 5, 5)

        #Draw progress bar
        painter.setFont(QFont("Courier New", 30))

        painter.setPen(QColor(0, 230, 255, 240))

        painter.drawText(0, ba_y + 70, w, 45, Qt.AlignCenter, f"{int(loading * 100)}%")

        self.draw_hud_frame(painter, w, h, passed_time)
        self.draw_boot_weather(painter, w, h)

    def draw_hud_frame(self, painter, w, h, passed_time):
        cyan = QColor(0, 200, 255, 150)
        dim = QColor(0, 150, 200, 70)
        bright = QColor(0, 220, 255, 220)

        painter.setBrush(Qt.NoBrush)

        # glow
        painter.setPen(QPen(QColor(0, 180, 255, 35), 5))

        painter.drawLine(40, 0, 260, 0)
        painter.drawLine(w - 40, 0, w - 260, 0)

        painter.drawLine(40, h, 260, h)
        painter.drawLine(w - 40, h, w - 260, h)

        # sharp
        painter.setPen(QPen(cyan, 1))

        # top left frame
        painter.drawLine(0, 0, 210, 0)
        painter.drawLine(210, 0, 255, 42)
        painter.drawLine(255, 42, 420, 42)

        painter.drawLine(0, 58, 180, 58)
        painter.drawLine(180, 58, 230, 105)
        painter.drawLine(230, 105, 420, 105)

        # top right frame
        painter.drawLine(w, 0, w - 210, 0)
        painter.drawLine(w - 210, 0, w - 255, 42)
        painter.drawLine(w - 255, 42, w - 420, 42)

        painter.drawLine(w, 58, w - 180, 58)
        painter.drawLine(w - 180, 58, w - 230, 105)
        painter.drawLine(w - 230, 105, w - 420, 105)

        # bottom left frame
        painter.drawLine(0, h, 210, h)
        painter.drawLine(210, h, 255, h - 42)
        painter.drawLine(255, h - 42, 420, h - 42)

        painter.drawLine(0, h - 58, 180, h - 58)
        painter.drawLine(180, h - 58, 230, h - 105)
        painter.drawLine(230, h - 105, 420, h - 105)

        # bottom right frame
        painter.drawLine(w, h, w - 210, h)
        painter.drawLine(w - 210, h, w - 255, h - 42)
        painter.drawLine(w - 255, h - 42, w - 420, h - 42)

        painter.drawLine(w, h - 58, w - 180, h - 58)
        painter.drawLine(w - 180, h - 58, w - 230, h - 105)
        painter.drawLine(w - 230, h - 105, w - 420, h - 105)

        # center top/bottom
        painter.setPen(QPen(dim, 1))

        painter.drawLine(470, 32, w // 2 - 170, 32)
        painter.drawLine(w // 2 + 170, 32, w - 470, 32)

        painter.drawLine(470, h - 32, w // 2 - 170, h - 32)
        painter.drawLine(w // 2 + 170, h - 32, w - 470, h - 32)

        # small top/bottom
        painter.setPen(QPen(QColor(0, 190, 255, 110), 1))

        for i in range(22):
            tx = w // 2 - 220 + i * 20
            th = 9 if i % 5 == 0 else 5

            painter.drawLine(tx, 28, tx, 28 + th)
            painter.drawLine(tx, h - 28, tx, h - 28 - th)

        # moving scan ticks
        move = int((passed_time * 120) % 260)

        painter.setPen(QPen(QColor(0, 245, 255, 190), 2))

        painter.drawLine(470 + move, 32, 510 + move, 32)
        painter.drawLine(w - 470 - move, h - 32, w - 510 - move, h - 32)

        # labels
        painter.setFont(QFont("Courier New", 11))
        painter.setPen(QColor(0, 200, 255, 180))

        painter.drawText(95, 38, "A.I. SYSTEMS")
        painter.drawText(w - 220, 38, "MOTION TRACKING")

        painter.drawText(95, h - 32, "PANEL")
        painter.drawText(w - 260, h - 32, "NETWORK CONFIG")

    def draw_boot_weather(self, painter, w, h):
        weather = self.weather_service.get_weather()

        x = 65
        y = 135

        temp = weather["temperature"]
        wind = weather["wind"]
        rain = weather["precipitation"]

        cyan = QColor(0, 220, 255, 210)
        bright = QColor(190, 250, 255, 240)
        dim = QColor(0, 150, 200, 170)

        # icon: cloud and sun
        iy = 44

        painter.setPen(QPen(cyan, 2))
        painter.setBrush(Qt.NoBrush)

        # sun
        painter.drawEllipse(x + 170, y + iy + 8, 28, 28)

        # cloud
        painter.drawArc(x + 118, y + iy + 30, 38, 30, 0, 180 * 16)
        painter.drawArc(x + 145, y + iy + 22, 42, 38, 0, 180 * 16)

        painter.drawLine(
            x + 120,
            y + iy + 45,
            x + 190,
            y + iy + 45
        )
        # temp
        painter.setFont(QFont("Courier New", 34))
        painter.setPen(bright)
        painter.drawText(x, y + 42, f"{temp}°")

        painter.setFont(QFont("Courier New", 12))
        painter.setPen(dim)
        painter.drawText(x + 92, y + 20, "CURRENT")
        painter.drawText(x + 70, y + 40, LOCATION_NAME.upper())

        painter.setFont(QFont("Courier New", 11))
        painter.setPen(cyan)
        painter.drawText(x, y + 75, f"WIND {wind} MPH")
        painter.drawText(x, y + 95, f"PRECIP {rain}")

        # thin divider
        painter.setPen(QPen(QColor(0, 180, 255, 90), 1))
        painter.drawLine(x, y + 110, x + 250, y + 110)

    def draw_glow(self, painter, cx, cy, radius):
        painter.setPen(Qt.NoPen)

        for i in range(5, 0, -1):
            r = radius + i * 12
            painter.setBrush(QColor(0, 80 + i * 8, 120 + i * 12, 16))
            painter.drawEllipse(int(cx - r),int(cy - r),int(r * 2),int(r * 2))

    def draw_core(self, painter, cx, cy, radius):
        painter.setPen(Qt.NoPen)

        # soft outer glow
        painter.setBrush(QColor(0, 200, 255, 65))
        glow_r = radius * 1.35
        painter.drawEllipse(int(cx - glow_r),int(cy - glow_r),int(glow_r * 2), int(glow_r * 2))

        # large glow
        painter.setBrush(QColor(0, 140, 255, 28))
        big_glow = radius * 1.9
        painter.drawEllipse(int(cx - big_glow),int(cy - big_glow), int(big_glow * 2), int(big_glow * 2))

        for i in range(6, 0, -1):
            aura_r = radius + (i * 7) + math.sin(self.t * 2.2) * 2

            alpha = 10 + i * 4

            painter.setBrush(QColor(0, 220, 255, alpha))
            painter.setPen(Qt.NoPen)

            painter.drawEllipse(int(cx - aura_r), int(cy - aura_r), int(aura_r * 2), int(aura_r * 2))

        # outer glass orb
        painter.setBrush(QColor(0, 35, 55, 150))
        painter.setPen(QPen(QColor(0, 220, 255, 230), 2))
        painter.drawEllipse(int(cx - radius), int(cy - radius),int(radius * 2), int(radius * 2))

        # middle ring
        mid = radius * 0.68
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(80, 230, 255, 190), 2))
        painter.drawEllipse(int(cx - mid),int(cy - mid),int(mid * 2),int(mid * 2))

        # inner core
        inner = radius * 0.28
        painter.setBrush(QColor(130, 245, 255, 210))
        painter.setPen(QPen(QColor(220, 255, 255, 240), 2))
        painter.drawEllipse(int(cx - inner), int(cy - inner), int(inner * 2), int(inner * 2))

        # inner tiny center
        center = radius * 0.10
        painter.setBrush(QColor(255, 255, 255, 230))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx - center), int(cy - center), int(center * 2),int(center * 2))

    def draw_music_panel(self, painter):
        music = self.state_manager.get_music()

        x = 50
        y = self.height() -520
        w = 390
        h = 145

        self.draw_panel(painter, x, y, w, h, "SPOTIFY")
        cyan_color = QColor(0, 220, 255, 220)
        b = QColor(180, 245, 255, 240)
        d = QColor(0, 130, 180, 220)

        painter.setBrush(QColor(0, 20, 32, 135))
        painter.setPen(QPen(QColor(0, 220, 255, 150), 1))
        painter.drawRoundedRect(x, y, w, h, 14, 14)

        painter.setPen(QPen(cyan_color, 2))
        painter.drawLine(x + 18, y, x + 85, y)
        painter.drawLine(x, y + 18, x, y + 70)
        painter.drawLine(x+w-85, y+h, x+w-18, y+h)
        painter.drawLine(x+w, y+h-70, x+w, y+h-18)

        painter.setFont(QFont("Courier New", 12))
        painter.setPen(cyan_color)
        painter.setPen(QPen(QColor(0, 220, 255, 80), 1))
        painter.drawLine(x+22, y+ 42, x+w-22, y+42)
        x1 = x + 75
        y1 = y+96
        r = 38

        painter.setBrush(QColor(0, 220, 255, 30))
        painter.setPen(QPen(QColor(0, 220, 255, 160), 2))
        painter.drawEllipse(x1-r, y1-r, r*2, r*2)

        painter.setBrush(Qt.NoBrush)
        for i in range(3):
            rr = r + 8 + i *7
            start = int((self.t * 110 + i * 95) * 16)
            s2 = int(65*16)
            painter.setPen(QPen(QColor(0, 220, 255, 130-i *25), 2))
            painter.drawArc(x1-rr, y1-rr, rr*2, rr*2, start, s2)

        t = QPolygon([QPoint(x1-9, y1-15), QPoint(x1-9, y1+15), QPoint(x1+17, y1)])
        painter.setBrush(b)
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(t)

        title = music.get("title", "No Track Selected")
        if len(title) > 30:
            title = title[:27] + "..."

        painter.setFont(QFont("Courier New", 16))
        painter.setPen(b)
        painter.drawText(x + 135, y + 82, title)

        painter.setFont(QFont("Courier New", 12))
        painter.setPen(d)
        painter.drawText(x + 135, y + 108, music.get("source", "SPOTIFY"))

        painter.setFont(QFont("Courier New", 12))
        painter.setPen(cyan_color)
        painter.drawText(x+135, y + 132, f"STATUS: {music.get("status", "IDLE")}")

        for i in range(22):
            b_h = int(8 + abs(math.sin(self.t * 4 + i* 0.7)) * 32)
            bx = x + 260 + i * 6
            by = y + 132 - b_h
            painter.fillRect(bx, by, 3, b_h, QColor(0, 220, 255, 150))

        d_x = x + 22 + int((math.sin(self.t *2) * 0.5 + 0.5) * (w-44))

        painter.setBrush(QColor(0, 255, 210, 220))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(d_x-3, y + h-18, 6, 6)

    def draw_hand_landmarks(self, painter):
        """
        Draws hand of the user

        Shows the hand points and connections
        when gesture control is active
        """

        #Exit if gesture is off
        if self.gesture is None:
            return

        if self.state == "SCANNING":
            return

        #Get the latest tracking data
        latest_data = self.gesture.get_latest()

        if not latest_data["hand_visible"]:
            return

        points = latest_data.get("points", [])

        if not points:
            return

        width = self.width()
        height = self.height()

        if latest_data["pinching"]:
            color = QColor(0, 255, 200, 240)
        else:
            color = QColor(0, 220, 255, 220)

        #Draw all of the hand connections
        hand = [
            (0,1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19,20),
            (5, 9), (9, 13), (13, 17)
        ]

        painter.setPen(QPen(color, 2))
        painter.setBrush(Qt.NoBrush)

        #Draw hand points
        for p1, p2 in hand:
            x1 = int(points[p1]["x"]*width)
            y1 = int(points[p1]["y"]*height)
            x2 = int(points[p2]["x"]*width)
            y2 = int(points[p2]["y"]*height)
            painter.drawLine(x1, y1, x2, y2)

        painter.setPen(Qt.NoPen)

        # Finger tips use larger circles
        # to make important landmarks easier to see
        for p3, p4 in enumerate(points):
            x = int(p4["x"]*width)
            y = int(p4["y"]*height)

            # Thumb, index, middle,
            # ring, and pinky tips
            if p3 in [4, 8, 12, 16, 20]:
                rad = 5
            else:
                rad = 3

            painter.setBrush(QColor(180, 255, 255, 230))
            painter.drawEllipse(x-rad, y-rad, rad*2, rad*2)

        if latest_data["pinching"]:
            i = points[8]
            t = points[4]

            x3 = int(i["x"]*width)
            y3 = int(i["y"]*height)

            x4 = int(t["x"]*width)
            y4 = int(t["y"]*height)

            x5 = (x3+x4)//2
            y5 = (y3+y4)//2

            #Highlight when user pinches
            painter.setBrush(QColor(0, 255, 200, 50))
            painter.setPen(QPen(QColor(0, 255, 200, 200), 2))
            painter.drawEllipse(x5-28, y5-28, 56, 56)

        if latest_data["pinching"]:
            painter.setBrush(QColor(0, 255, 200, 45))
            painter.setPen(QPen(QColor(0, 255, 200, 180), 2))
            painter.drawEllipse(x-38, y-38, 76, 76)

    def draw_rings(self, painter, cx, cy, radius):
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(0, 160, 220, 170), 1))

        # rings
        for i in range(3):
            ring_radius = radius + 15 + i * 16
            points = []

            for j in range(0, 360, 8):
                angle = math.radians(j) + self.angle * (1 + i * 0.35)
                wobble = math.sin(angle * 3 + self.angle * 4) * 5
                r = ring_radius + wobble

                x = cx + math.cos(angle) * r
                y = cy + math.sin(angle) * r
                points.append((x, y))

            for a, b in zip(points, points[1:] + points[:1]):
                painter.drawLine(int(a[0]), int(a[1]), int(b[0]), int(b[1]))

        #Arc creation
        painter.setPen(QPen(QColor(120, 240, 255, 180), 2))

        arc_r = radius + 42

        for i in range(4):
            start = int((self.angle * 40 + i * 90) * 16)
            span = int(38 * 16)

            painter.drawArc(int(cx - arc_r),int(cy - arc_r), int(arc_r * 2), int(arc_r * 2), start, span)

        #Target lines
        painter.setPen(QPen(QColor(0, 200, 255, 140), 1))

        for i in range(12):
            angle = (math.tau / 12) * i + self.angle * 0.5

            inner = radius + 35
            outer = radius + 58

            x1 = cx + math.cos(angle) * inner
            y1 = cy + math.sin(angle) * inner

            x2 = cx + math.cos(angle) * outer
            y2 = cy + math.sin(angle) * outer

            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def draw_particles(self, painter, cx, cy):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 140, 200, 160))

        for p in self.particles:
            angle = p["angle"] + self.t * p["speed"]
            dist = p["distance"] + math.sin(self.t * 2 + p["angle"]) * 10

            x = cx + math.cos(angle) * dist
            y = cy + math.sin(angle) * dist

            painter.drawEllipse(int(x), int(y), p["size"], p["size"])

    def draw_state_text(self, painter, cx, cy):
        painter.setFont(QFont("Courier New", 18))
        painter.setPen(QColor(0, 180, 255, 220))

        text = self.state
        rect_width = 220

        painter.drawText(int(cx - rect_width // 2), int(cy + 180), rect_width, 30, Qt.AlignCenter, text)

    def draw_calendar_panel(self, painter):
        x = 50
        y = 45
        w = 330
        h = 250

        self.draw_panel(painter, x, y, w, h, "Calendar")

        now = datetime.datetime.now()
        month = now.strftime("%B %Y")

        painter.setFont(QFont("Courier New", 18))
        painter.setPen(QColor(150, 235, 255, 230))
        painter.drawText(x, y + 50, w, 25, Qt.AlignCenter, month)

        painter.setFont(QFont("Courier New", 13))
        painter.setPen(QColor(0, 150, 200, 220))

        days = ["M", "T", "W", "T", "F", "S", "S"]

        start_x = x + 42
        start_y = y + 78
        cell = 36
        row_gap = 22

        for i, day in enumerate(days):
            painter.drawText(start_x + i * cell, start_y + 8, day)

        cal = calendar.monthcalendar(now.year, now.month)

        painter.setFont(QFont("Courier New", 14))

        for row, week in enumerate(cal):
            for col, day in enumerate(week):
                if day == 0:
                    continue

                px = start_x + col * cell
                py = start_y + 28 + row * row_gap

                if day == now.day:
                    circle_size = 30

                    painter.setBrush(QColor(0, 210, 255, 70))
                    painter.setPen(QPen(QColor(0, 220, 255, 220), 2))

                    painter.drawEllipse(int(px - circle_size / 2 + 6), int(py - circle_size / 2 - 7), circle_size, circle_size)

                    painter.setPen(QColor(220, 255, 255, 255))
                else:
                    painter.setPen(QColor(150, 235, 255, 210))

                painter.drawText(px, py, str(day))

    def draw_scan_overlay(self, painter):
        if self.state != "SCANNING":
            return

        w = self.width()
        h = self.height()

        # full screen cyan
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 180, 255, 22))
        painter.drawRect(0, 0, w, h)

        # moving scan bar
        scan_y = int((self.t * 420) % h)

        painter.setBrush(QColor(0, 220, 255, 55))
        painter.drawRect(0, scan_y, w, 4)

        # scan lines
        painter.setPen(QPen(QColor(0, 160, 220, 35), 1))
        for y in range(0, h, 8):
            painter.drawLine(0, y, w, y)

        # corner blocks
        painter.setPen(QPen(QColor(0, 220, 255, 210), 3))

        size = 70
        pad = 40

        # top left
        painter.drawLine(pad, pad, pad + size, pad)
        painter.drawLine(pad, pad, pad, pad + size)

        # top right
        painter.drawLine(w - pad, pad, w - pad - size, pad)
        painter.drawLine(w - pad, pad, w - pad, pad + size)

        # bottom left
        painter.drawLine(pad, h - pad, pad + size, h - pad)
        painter.drawLine(pad, h - pad, pad, h - pad - size)

        # bottom right
        painter.drawLine(w - pad, h - pad, w - pad - size, h - pad)
        painter.drawLine(w - pad, h - pad, w - pad, h - pad - size)

    def draw_target_overlay(self, painter):
        objects = self.vision.get_live_objects()

        if not objects:
            return

        w = self.width()
        h = self.height()

        sx = w / 640
        sy = h / 480

        painter.setFont(QFont("Courier New", 16))

        for obj in objects:
            name = f'{obj["name"].upper()} {int(obj["confidence"] * 100)}%'
            x1, y1, x2, y2 = obj["box"]

            x1 = int(x1 * sx)
            y1 = int(y1 * sy)
            x2 = int(x2 * sx)
            y2 = int(y2 * sy)

            self.draw_target_box(painter, x1, y1, x2, y2)

            painter.setPen(QColor(180, 240, 255, 240))
            painter.drawText(x1, max(20, y1 - 8), name)

    def draw_target_box(self, painter, x1, y1, x2, y2):
        size = 22

        painter.setPen(QPen(QColor(0, 220, 255, 230), 2))

        painter.drawLine(x1, y1, x1 + size, y1)
        painter.drawLine(x1, y1, x1, y1 + size)

        painter.drawLine(x2, y1, x2 - size, y1)
        painter.drawLine(x2, y1, x2, y1 + size)

        painter.drawLine(x1, y2, x1 + size, y2)
        painter.drawLine(x1, y2, x1, y2 - size)

        painter.drawLine(x2, y2, x2 - size, y2)
        painter.drawLine(x2, y2, x2, y2 - size)

    def draw_voice_waveform(self, painter, cx, cy, radius):
        if self.state != "SPEAKING":
            return

        painter.setPen(QPen(QColor(0, 220, 255, 180), 2))

        bars = 48
        for i in range(bars):
            angle = (math.tau / bars) * i

            wave = math.sin(self.t * 12 + i * 0.7) * 0.5 + 0.5
            length = 18 + wave * 45

            inner = radius + 75
            outer = inner + length

            x1 = cx + math.cos(angle) * inner
            y1 = cy + math.sin(angle) * inner
            x2 = cx + math.cos(angle) * outer
            y2 = cy + math.sin(angle) * outer

            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

class JarvisQtWindow(QMainWindow):
    """
    Main ATLAS window

    This class creates the full screen window,
    loads the map, starts voice control,
    creates the HUD, and connects the gesture control
    to ATLAS

    FEATURES:
        1. Full screen window
        2. Map view
        3. Voice controller
        4. HUD
        5. Gesture control
        6. Vision scan support
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIS")
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.map_view = QWebEngineView()
        self.setCentralWidget(self.map_view)
        self.last_map_state = None

        settings = self.map_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)

        map_path = os.path.abspath("map/map.html")
        self.map_view.loadFinished.connect(lambda ok: print("Map loaded:", ok))
        self.map_view.load(QUrl.fromLocalFile(map_path))
        self.state = JarvisState()
        self.voice = VoiceController(self.state)
        self.voice.window = self
        intro = self.voice.center.ai.ask("Introduce yourself like JARVIS waking up for the first time, do not refer to the user as master or tony stark, don't use any special characters, and don't be overly silly, you have a strong funny personality and are witty,  Keep it short.")

        self.voice.tts.speak(intro)
        self.gesture = None
        self.settings = SettingsService()
        self.state.settings = self.settings
        # self.voice.center.vision.frame_provider = self.gesture.get_latest_frame
        self.overlay = HUDOverlay(self.state, None, self.voice.center.vision)
        self.overlay.setParent(self)
        self.overlay.setGeometry(self.rect())
        self.face_v = QWebEngineView(self)
        self.face_v.show()
        self.overlay.raise_()
        face_settings = self.face_v.settings()
        face_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        face_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        face_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        face_settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)

        face_path = os.path.abspath("map/face3d.html")
        self.face_v.load(QUrl.fromLocalFile(face_path))
        self.face_v.setStyleSheet("background: transparent; border: none;")
        self.face_v.setAttribute(Qt.WA_TranslucentBackground)
        self.face_v.page().setBackgroundColor(Qt.transparent)
        self.showFullScreen()
        self.face_v.setGeometry(self.width() - 450, self.height() // 2 - 215, 430, 400)
        self.speak_boot_intro()
        self.map_state_timer = QTimer()
        self.map_state_timer.timeout.connect(self.sync_map_state)
        self.map_state_timer.start(150)
        self.last_gesture_x = None
        self.last_gesture_y = None
        self.gesture_timer = QTimer()
        self.gesture_timer.timeout.connect(self.sync_gesture_to_map)
        self.gesture_timer.start(60)
        self.last_gesture_a = None
        self.scan_running = False
        self.scan_cooldown_until = 0
        self.current_mode = self.settings.get("default_mode", "MAP")
        self.swipe_start_x = None
        self.swipe_start_time = None
        self.last_open_palm_time = 0
        self.modes = ["MAP", "HUD", "VOICE", "SCAN"]
        self.gesture_cooldown = 0
        self.state.window = self

    def create_status_report(self):
        """
        Creates a system report that ATLAS will Speak

        combines weather, system stats, gesture status, mode,
        and home data into one ATLAS response
        """

        #Get weather values
        weather = self.voice.center.weather.get_weather()
        temp = weather.get("temperature", "unknown")
        precipitation = weather.get("precipitation", "unknown")
        wind = weather.get("wind", "unknown")

        #Get system values
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        #Check if gesture is online or offline
        if self.gesture is None:
            gesture = "offline"
        else:
            gesture = "online"
        mode = self.current_mode.lower()

        #Try to include home status
        home = ""

        try:
            if hasattr(self.voice.center, "home"):
                home = self.voice.center.home.report()

        except:
            home = "Home systems unavailable."

        #Build the report
        report = (
            f"All primary systems are operational. "
            f"Current mode is {mode} mode. "
            f"Gesture controls are {gesture}. "
            f"The current temperature is {temp} degrees, "
            f"with precipitation at {precipitation} and wind around {wind} miles per hour. "
            f"CPU utilization is {cpu} percent. "
            f"Memory usage is {int(ram)} percent. "
            f"{home}"
            f"Awaiting further instruction."
        )

        return report

    def speak_boot_intro(self):
        """
        Creates the boot introduction

        Uses the AI service to generate
        a short startup message for ATLAS
        """

        weather = self.voice.center.weather.get_weather()
        now = datetime.datetime.now().strftime("%I:%M %p")

        #Create the prompt
        prompt = f"""
        You are Atlas, an advanced AI assistant and operating intelligence.

        You are booting up for the user.

        Write a short startup introduction in first person.

        Style:
            1. Sound human, calm, confident, and slightly futuristic
            2. Speak about who you are, what you are interested in, and how you can help
            3. Mention that you can help with coding, system control, screen analysis, vision, and workflow support
            4. Keep it natural, not robotic
            5. No jokes
            6. No emojis
            7. Maximum 7 sentences
        """

        #Ask AI for the introduction
        intro = self.voice.center.ai.ask(prompt)

        #Speak the intro
        self.voice.tts.speak(intro)

    def start_gesture_control(self):
        """
        Starts gesture control

        Creates the hand tracking service
        and connects it to the HUD and vision system
        """

        #Don't start the service again
        if self.gesture is not None:
            return "Gesture control is already active."

        #Start the hand tracking service
        self.gesture = HandTrackingService()
        self.overlay.gesture = self.gesture
        self.voice.center.vision.frame_provider = self.gesture.get_latest_frame

        return "Gesture control activated."

    def stop_gesture_control(self):
        """
        Stops gesture control

        Shuts down hand tracking and clears
        saved gesture values
        """

        #Don't do anything if it's already off
        if self.gesture is None:
            return "Gesture control is already inactive."

        #Stop hand tracking
        self.gesture.shutdown()

        #Clear all the values
        self.gesture = None
        self.overlay.gesture = None
        self.last_gesture_x = None
        self.last_gesture_y = None
        self.last_gesture_a = None

        return "Gesture control deactivated."

    def change_mode(self, direction):
        i = self.modes.index(self.current_mode)

        if direction == "RIGHT":
            i = (i + 1) % len(self.modes)
        elif direction == "LEFT":
            i = (i - 1) % len(self.modes)

        self.current_mode = self.modes[i]
        print("Mode: ", self.current_mode)
    def sync_map_state(self):
        current_state = self.state.get()

        if current_state == self.last_map_state:
            return

        self.last_map_state = current_state

        safe_state = current_state.replace('"', '')

        self.map_view.page().runJavaScript(f'window.setAtlasState("{safe_state}");')

    def resizeEvent(self, event):
        if hasattr(self, "overlay"):
            self.overlay.setGeometry(self.rect())
            self.overlay.raise_()

        if hasattr(self, "face_v"):
            self.face_v.setGeometry(self.width() - 450, self.height() // 2 - 300, 470, 560)

        super().resizeEvent(event)

    def closeEvent(self, event):
        if hasattr(self, "voice"):
            self.voice.shutdown()
        if hasattr(self, "gesture"):
            self.gesture.shutdown()
        event.accept()

    def sync_gesture_to_map(self):
        """
        Sends gesture movement to the map

        Also uses fist gesture to scan for objects
        """
        # Exit if gesture control is off
        if self.gesture is None:
            return

        #Get the latest hand points
        data = self.gesture.get_latest()

        gesture = data.get("gesture", "None")

        time_now = datetime.datetime.now().timestamp()

        gesture = data.get("gesture", "NONE")

        #Start scanning when the fist is detected
        if gesture == "FIST" and self.last_gesture_a != "FIST" and not self.scan_running:
            self.last_gesture_a = "FIST"
            self.scan_running = True

            self.state.set("SCANNING")

            frame = self.gesture.get_latest_frame()
            result = self.voice.center.vision.scan(frame)

            self.state.set_scan_results(result["objects"])

            self.voice.tts.speak(result["text"])

            self.scan_running = False
            return

        if gesture != "FIST":
            self.last_gesture_a = gesture

        if not data["hand_visible"]:
            self.last_gesture_x = None
            self.last_gesture_y = None
            return

        x = data["x"]
        y = data["y"]

        if self.last_gesture_x is None:
            self.last_gesture_x = x
            self.last_gesture_y = y
            return

        x2 = x - self.last_gesture_x
        y2 = y - self.last_gesture_y

        self.last_gesture_x = x
        self.last_gesture_y = y

        #Ignore any small movement
        zone = 0.01

        if abs(x2) < zone:
            x2 = 0

        if abs(y2) < zone:
            y2 = 0

        pinching = "true" if data["pinching"] else "false"

        #Send that data to the map
        self.map_view.page().runJavaScript(f"window.handleGesture({x2}, {y2}, {pinching});")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = JarvisQtWindow()
    window.show()

    sys.exit(app.exec())