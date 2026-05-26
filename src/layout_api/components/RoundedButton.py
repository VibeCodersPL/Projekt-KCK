from kivy.graphics import RoundedRectangle, Color
from kivy.uix.button import Button


class RoundedButton(Button):
    def __init__(self, bg_color=(0.2, 0.6, 0.8, 1), radius=20,bg_image = None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bg_color = bg_color
        self.radius = radius
        self.bg_image = bg_image

        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius],source=self.bg_image)

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size