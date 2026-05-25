import src.detection.excersises as ex
from src.layout_api.TwoCameraFrameWindow import TwoCameraFrameWindow as TCFW
class Trening_Jednego_Elementu(TCFW):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screenExcersise = ex.LowReady()

    def on_start_click(self):
        print("Kliknięto START")
        self.set_title_text("TRENING ROZPOCZĘTY", color=(0.2, 1, 0.2, 1))

    def on_rest_click(self):
        print("Kliknięto ODPOCZYNEK")
        self.set_title_text("CZAS NA PRZERWE", color=(0.2, 0.6, 1, 1))

    def update_frame(self, dt):
        super().update_frame(dt)