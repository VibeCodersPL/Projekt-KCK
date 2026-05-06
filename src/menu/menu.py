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

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Trening_Wspierany import *
from Wzorowy_Pokaz import *
from Trening_Jednego_Elementu import *
from RoundedButton import *
from src.base_detection import *

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        wid = Widget()
        layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(350, 320), spacing=20)
        main_text = Label(
            text='Cyber-Trener',
            font_size='32sp',
            bold=True,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(main_text)
        self.screen_mapping = {
            'Trening wspierany': 'Trening wspierany',
            'Trening jednego elementu': 'TreningJednegoElementu',
            'Wzorowy pokaz': 'WzorowyPokaz'
        }
        self.menu_buttons = []
        for mode in self.screen_mapping.keys():
            button = RoundedButton(
                text=mode,
                font_size='26sp',
                color=(1, 1, 1, 1),
                bg_color=(0.15, 0.45, 0.85, 1),
                radius=30
            )
            button.bind(on_press=self.change_screen)
            layout.add_widget(button)
            self.menu_buttons.append(button)
        root = AnchorLayout(anchor_x='center', anchor_y='center')
        root.add_widget(wid)
        root.add_widget(layout)
        self.add_widget(root)
        self.cursor = Image(
            source='../assets/lapka1.png',
            size_hint=(None, None),
            size=(100, 100),
            pos = (-100,-100)
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
        self.detector = BaseDetection()
        self.cap = cv2.VideoCapture(0)
        self.update = Clock.schedule_interval(self.update_frame, 1/20)

    def on_leave(self):
        if self.update:
            self.update.cancel()
        if self.cap:
            self.cap.release()
        if self.detector:
            self.detector.close()
        self.clean()
        self.button_hover = None
        self.cursor.pos=(-100,-100)

    def get_hand_coords(self, landmarks):
        right_hand = landmarks[19]
        if right_hand.visibility > 0:
            return (right_hand.x, right_hand.y)
        return None

    def update_frame(self,dt):
        if not self.cap or not self.cap.isOpened():
            return

        temp, frame = self.cap.read()
        if not temp:
            return
        frame = cv2.flip(frame, 1)
        _, result = self.detector.process_frame(frame)
        cursor_pos = None
        if result and result.pose_landmarks:
            cursor_pos = self.get_hand_coords(result.pose_landmarks[0])

        if cursor_pos is not None:
            x, y = cursor_pos
            win_x = x * Window.width
            win_y = (1-y) * Window.height
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
                        self.fill_color = Color(0.1,0.8,0.2,0.5)
                        self.fill_rectangle = RoundedRectangle(
                            pos=self.button_hover.pos,
                            size=(self.button_hover.width,0),
                            radius=[30,30,30,30],
                        )
                else:
                    elapsed_time = time.time() - self.button_hover_start
                    progress = min(1.0,elapsed_time/2.0)
                    if self.fill_rectangle:
                        new_height  = self.button_hover.height * progress
                        self.fill_rectangle.size = (self.button_hover.width,new_height)

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
            self.cursor.pos = (-100,-100)
            if self.button_hover is not None:
                self.clean()
                self.button_hover = None
                self.cursor.source = "../assets/lapka1.png"

    def change_screen(self, instance):
        target_screen = self.screen_mapping.get(instance.text)
        if target_screen:
            self.manager.current = target_screen

class Menu(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(TreningWspierany(name='Trening wspierany'))
        sm.add_widget(Trening_Jednego_Elementu(name='TreningJednegoElementu'))
        sm.add_widget(WzorowyPokaz(name='WzorowyPokaz'))
        return sm


if __name__ == '__main__':
    Menu().run()