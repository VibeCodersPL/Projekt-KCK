import vision.excersises as ex
from ui.screens.two_camera_screen import TwoCameraScreen as TCFW
class SingleElementTrainingScreen(TCFW):
    def __init__(self, screen_excersise:ex.Exercise, **kwargs):
        super().__init__(screen_excersise=screen_excersise, **kwargs)

    def on_start_click(self):
        print("Kliknięto START")
        self.set_title_text("TRENING ROZPOCZĘTY", color=(0.2, 1, 0.2, 1))

    def on_rest_click(self):
        print("Kliknięto ODPOCZYNEK")
        self.set_title_text("CZAS NA PRZERWE", color=(0.2, 0.6, 1, 1))

    def update_frame(self, dt):
        super().update_frame(dt)