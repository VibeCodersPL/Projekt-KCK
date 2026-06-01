from kivy.core.window import Window
from kivy.properties import partial
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen,NoTransition
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import RoundedRectangle, Color
from kivy.uix.image import Image
from kivy.clock import Clock

from detection.base_detection import *
from layout_api.components.RoundedButton import RoundedButton
from windows.PostawaStojaca import *
from windows.PostawaKleczaca import *


class WzorowyPokazScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        wid = Widget()
        layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(1000, 630), spacing=20)
        main_text = Label(
            text='Wzorowy Pokaz',
            font_size='50sp',
            bold=True,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(main_text)
        self.screen_mapping = {
            'Postawa Stojąca': 'PostawaStojaca',
            'Postawa klęcząca': 'PostawaKleczaca',
            'Menu': 'menu'
        }
        self.menu_buttons = []
        blocks_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=20)
        btn_stojaca = RoundedButton(
            text='Postawa Stojąca',
            font_size='36sp',
            color=(1, 1, 1, 1),
            bg_color=(0.15, 0.45, 0.85, 1),
            radius=30,
            bg_image="../assets/Postawa1.png"
        )
        btn_stojaca.bind(on_press=self.change_screen)
        blocks_layout.add_widget(btn_stojaca)
        self.menu_buttons.append(btn_stojaca)

        btn_kleczaca = RoundedButton(
            text='Postawa klęcząca',
            font_size='36sp',
            color=(1, 1, 1, 1),
            bg_color=(0.15, 0.45, 0.85, 1),
            radius=30,
            bg_image="../assets/Postawa2.png"
        )
        btn_kleczaca.bind(on_press=self.change_screen)
        blocks_layout.add_widget(btn_kleczaca)
        self.menu_buttons.append(btn_kleczaca)

        layout.add_widget(blocks_layout)
        btn_menu = RoundedButton(
            text='Menu',
            font_size='36sp',
            color=(1, 1, 1, 1),
            bg_color=(0.85, 0.15, 0.15, 1),
            radius=30,
            size_hint=(1, 0.3)
        )
        btn_menu.bind(on_press=self.change_screen)
        layout.add_widget(btn_menu)
        self.menu_buttons.append(btn_menu)
        root = AnchorLayout(anchor_x='center', anchor_y='center')
        root.add_widget(wid)
        root.add_widget(layout)
        self.add_widget(root)
        self.cursor = Image(
            source='../assets/lapka1.png',
            size_hint=(None, None),
            size=(100, 100),
            pos=(-100, -100)
        )
        self.add_widget(self.cursor)
        self.detector = None
        self.cap = None
        self.update = None
        self.button_hover = None
        self.button_hover_start = None
        self.fill_color = None
        self.fill_rectangle = None

    def clean(self):
        if self.button_hover and self.fill_color and self.fill_rectangle:
            if self.fill_color in self.button_hover.canvas.after.children:
                self.button_hover.canvas.after.remove(self.fill_color)
            if self.fill_rectangle in self.button_hover.canvas.after.children:
                self.button_hover.canvas.after.remove(self.fill_rectangle)
        self.fill_color = None
        self.fill_rectangle = None

    def on_enter(self):
        self.detector = self.manager.shared_detector
        Clock.schedule_once(self._late_camera_init, 0.2)

    def _late_camera_init(self, dt):
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            self.update = Clock.schedule_interval(self.update_frame, 1 / 30)
        else:
            print("Kamera nadal zablokowana przez system.")

    def on_leave(self):
        if self.update:
            self.update.cancel()
            self.update = None
        if self.cap:
            self.cap.release()
            self.cap = None
        self.detector = None

        self.clean()
        self.button_hover = None
        self.cursor.pos = (-100, -100)
        self.cursor.source = "../assets/lapka1.png"

    def update_frame(self, dt):
        if not self.cap or not self.cap.isOpened():
            return

        temp, frame = self.cap.read()
        if not temp:
            return
        frame = cv2.flip(frame, 1)
        _, result = self.detector.process_frame(frame)
        cursor_pos = None
        cursor_pos = self.detector.getLandmarkCords(19);

        if cursor_pos is not None:
            x, y = cursor_pos
            win_x = x * Window.width
            win_y = (1 - y) * Window.height
            self.cursor.pos = (win_x - self.cursor.width / 2, win_y - self.cursor.height / 2)
            collision = None
            for button in self.menu_buttons:
                if button.collide_point(win_x, win_y):
                    collision = button
                    break

            if collision:
                if self.button_hover != collision:
                    self.clean()
                    self.button_hover = collision
                    self.button_hover_start = time.time()
                    self.cursor.source = "../assets/lapka2.png"
                    with self.button_hover.canvas.after:
                        self.fill_color = Color(0.1, 0.8, 0.2, 0.5)
                        self.fill_rectangle = RoundedRectangle(
                            pos=self.button_hover.pos,
                            size=(self.button_hover.width, 0),
                            radius=[30, 30, 30, 30],
                        )
                else:
                    elapsed_time = time.time() - self.button_hover_start
                    progress = min(1.0, elapsed_time / 2.0)
                    if self.fill_rectangle:
                        new_height = self.button_hover.height * progress
                        self.fill_rectangle.size = (self.button_hover.width, new_height)

                        if elapsed_time > 2.0:
                            self.clean()
                            self.change_screen(collision)
                            self.button_hover = None
                            self.cursor.source = "../assets/lapka1.png"
            else:
                if self.button_hover is not None:
                    self.clean()
                    self.button_hover = None
                    self.cursor.source = "../assets/lapka1.png"
        else:
            self.cursor.pos = (-100, -100)
            if self.button_hover is not None:
                self.clean()
                self.button_hover = None
                self.cursor.source = "../assets/lapka1.png"

    def change_screen(self, instance):
        target_screen = self.screen_mapping.get(instance.text)
        if target_screen:
            self.manager.current = target_screen


class WzorowyPokaz(App):

    def build(self):
        Window.fullscreen = 'auto'
        sm = ScreenManager(transition=NoTransition())
        sm.shared_detector = BaseDetection()
        sm.add_widget(WzorowyPokazScreen(name='WzorowyPokaz'))
        sm.add_widget(PostawaStojaca(name='PostawaStojaca'))
        sm.add_widget(PostawaKleczaca(name='PostawaKleczaca'))
        return sm


if __name__ == '__main__':
    WzorowyPokaz().run()