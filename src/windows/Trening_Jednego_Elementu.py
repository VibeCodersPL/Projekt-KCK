import detection.excersises as ex
from src.layout_api.TwoCameraFrameWindow import TwoCameraFrameWindow as TCFW
from src.layout_api.components.RoundedButton import RoundedButton
from kivy.core.window import Window

class Trening_Jednego_Elementu(TCFW):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screenExcersise = ex.LowReady()

        self.hover_start_frames = 0
        self.hover_rest_frames = 0
        self.HOVER_THRESHOLD = 30

        self.setup_custom_ui()

    def setup_custom_ui(self):
        """Dodaje obiektowe przyciski do głównego layoutu"""

        self.btn_start = RoundedButton(
            text="START",
            font_size='24sp',
            bg_color=(0, 0.7, 0, 1),
            radius=10,
            size_hint=(0.15, 0.1),
            pos_hint={'x': 0.02, 'y': 0.6}
        )

        self.btn_rest = RoundedButton(
            text="ODPOCZYNEK",
            font_size='24sp',
            bg_color=(0.15, 0.45, 0.85, 1),
            radius=10,
            size_hint=(0.15, 0.1),
            pos_hint={'x': 0.2, 'y': 0.6}
        )

        self.add_ui_element(self.btn_start)
        self.add_ui_element(self.btn_rest)