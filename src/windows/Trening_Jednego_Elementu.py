import detection.excersises as ex
from src.layout_api.TwoCameraFrameWindow import TwoCameraFrameWindow as TCFW
from src.layout_api.components.RoundedButton import RoundedButton
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle

class Trening_Jednego_Elementu(TCFW):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screenExcersise = ex.LowReady()

        self.hover_start_frames = 0
        self.hover_rest_frames = 0
        self.HOVER_THRESHOLD = 30

        self.setup_custom_ui()

    def setup_custom_ui(self):
        """Dodaje przyciski do głównego layoutu"""

        self.btn_start = RoundedButton(
            text="START",
            font_size='24sp',
            bg_color=(0, 0.7, 0, 1),
            radius=10,
            size_hint=(0.15, 0.1),
            pos_hint={'x': 0.02, 'y': 0.6}
        )

        with self.btn_start.canvas.after:
            Color(0, 1, 0, 0.5)
            self.start_rect = RoundedRectangle(pos=self.btn_start.pos, size=(0, 0), radius=[10])

        self.btn_rest = RoundedButton(
            text="ODPOCZYNEK",
            font_size='24sp',
            bg_color=(0.15, 0.45, 0.85, 1),
            radius=10,
            size_hint=(0.15, 0.1),
            pos_hint={'x': 0.2, 'y': 0.6}
        )

        with self.btn_rest.canvas.after:
            Color(0, 1, 0, 0.5)
            self.rest_rect = RoundedRectangle(pos=self.btn_rest.pos, size=(0, 0), radius=[10])

        self.add_ui_element(self.btn_start)
        self.add_ui_element(self.btn_rest)

    def handle_hover(self):
        """Sprawdza, czy nadgarstki znajdują się nad przyciskami"""
        if not self.detector:
            return

        wrists = []
        for idx in [15, 16]:
            lm = self.detector.getLandmarkCords(idx)
            if lm:
                kivy_x = lm[0] * Window.width
                kivy_y = (1.0 - lm[1]) * Window.height
                wrists.append((kivy_x, kivy_y))

        start_hovered = False
        rest_hovered = False

        for x, y in wrists:
            if self.btn_start.collide_point(x, y):
                start_hovered = True
            if self.btn_rest.collide_point(x, y):
                rest_hovered = True

        # Logika licznika dla start
        if start_hovered:
            if self.hover_start_frames >= 0:
                self.hover_start_frames += 1
                if self.hover_start_frames >= self.HOVER_THRESHOLD:
                    self.on_start_click()
                    self.hover_start_frames = -30
        else:
            self.hover_start_frames = max(0,
            self.hover_start_frames - 2) \
            if self.hover_start_frames > 0 \
            else self.hover_start_frames

        if self.hover_start_frames < 0:
            self.hover_start_frames += 1

        # Logika licznika dla odpoczynek
        if rest_hovered:
            if self.hover_rest_frames >= 0:
                self.hover_rest_frames += 1
                if self.hover_rest_frames >= self.HOVER_THRESHOLD:
                    self.on_rest_click()
                    self.hover_rest_frames = -30
        else:
            self.hover_rest_frames = max(0, self.hover_rest_frames - 2) \
                if self.hover_rest_frames > 0 else self.hover_rest_frames

        if self.hover_rest_frames < 0:
            self.hover_rest_frames += 1

    def on_start_click(self):
        print("Kliknięto START")
        self.set_title_text("TRENING ROZPOCZĘTY", color=(0.2, 1, 0.2, 1))

    def on_rest_click(self):
        print("Kliknięto ODPOCZYNEK")
        self.set_title_text("CZAS NA PRZERWE", color=(0.2, 0.6, 1, 1))

    def update_frame(self, dt):
        super().update_frame(dt)
        self.handle_hover()