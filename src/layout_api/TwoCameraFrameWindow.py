from kivy.properties import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import detection.excersises as Ex
from kivy.graphics import Color, RoundedRectangle
from src.layout_api.components.RoundedButton import RoundedButton


class TwoCameraFrameWindow(Screen):
    screenExcersise: Ex.Exercise = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.landmarksFront = None
        self.landmarksSide = None

        self.hover_start_frames = 0
        self.hover_rest_frames = 0
        self.HOVER_THRESHOLD = 30

        self.main_layout = FloatLayout()

        self.cameras_layout = BoxLayout(orientation="horizontal", spacing=15, size_hint=(1, 0.8),
                                        pos_hint={'center_y': 0.45})
        self.camera_view = Image(size_hint=(1, 1), allow_stretch=True)
        self.camera_view2 = Image(size_hint=(1, 1), allow_stretch=True)
        self.cameras_layout.add_widget(self.camera_view)
        self.cameras_layout.add_widget(self.camera_view2)

        self.ui_layer = FloatLayout()

        btn = Button(text="Powrot do Menu", size_hint=(None, None), size=(200, 50))
        btn.bind(on_press=partial(self.change_screen, 'menu'))

        self.text_box = Label(
            size_hint=(0.6, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.98},
            font_size='36sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        self.text_box.bind(size=self.text_box.setter('text_size'))

        self.ui_layer.add_widget(btn)
        self.ui_layer.add_widget(self.text_box)

        self._setup_base_buttons()

        self.main_layout.add_widget(self.cameras_layout)
        self.main_layout.add_widget(self.ui_layer)
        self.add_widget(self.main_layout)

    def _setup_base_buttons(self):
        """Metoda budująca wspólne przyciski treningowe (START i ZAPISZ)"""
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

        self.btn_save = RoundedButton(
            text="ZAPISZ",
            font_size='24sp',
            bg_color=(0.4, 0.4, 0.4, 1),
            radius=10,
            size_hint=(0.15, 0.1),
            pos_hint={'right': 0.98, 'y': 0.6}
        )
        with self.btn_save.canvas.after:
            Color(0, 1, 0, 0.5)
            self.save_rect = RoundedRectangle(pos=self.btn_save.pos, size=(0, 0), radius=[10])

        self.add_ui_element(self.btn_start)
        self.add_ui_element(self.btn_save)

    def add_ui_element(self, widget):
        self.ui_layer.add_widget(widget)

    def remove_ui_element(self, widget):
        self.ui_layer.remove_widget(widget)

    def set_title_text(self, text, color=(1, 1, 1, 1)):
        self.text_box.text = text
        self.text_box.color = color

    def change_screen(self, target_screen, instance):
        self.manager.current = target_screen

    def on_enter(self):
        self.detector = self.manager.shared_detector
        Clock.schedule_once(self._late_camera_init, 0.2)

    def _late_camera_init(self, dt):
        self.cap = cv2.VideoCapture(0)
        self.cap2 = cv2.VideoCapture(2)

        if(not self.cap2 or not self.cap2.isOpened()):
           self.cap2 = self.cap 

        if self.cap.isOpened() or self.cap2.isOpened():
            self.update_event = Clock.schedule_interval(self.update_frame, 1/30)
        else:
            print("Kamera nadal zablokowana przez system.")

    def update_frame(self, dt):
            if not self.cap or not self.cap.isOpened() and not self.cap2 or not self.cap2.isOpened():
                return

            if(self.cap.isOpened()):
                self.camera_view.texture, self.landmarksFront = self.update_camera(self.cap)
                
            if(self.cap2.isOpened()):
                self.camera_view2.texture, self.landmarksSide = self.update_camera(self.cap2, True)

    def update_camera(self, cap, isSide:bool = False):
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)

            processed_frame, result = self.detector.process_frame(frame)
            landmarks = self.detector.getLandmarks()

            processed_frame = self.process_cv_frame(processed_frame, isSide)

            buf = cv2.flip(processed_frame, 0).tobytes()

            texture = Texture.create(
                size=(processed_frame.shape[1], processed_frame.shape[0]),
                colorfmt='bgr'
            )

            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            return texture, landmarks

    def process_cv_frame(self, frame, isSide: bool):
        return frame

    def on_leave(self):
        """Uruchamiane przy wychodzeniu - zwalnianie zasobów"""
        if self.update_event:
            self.update_event.cancel()
        if self.cap:
            self.cap.release()
        if self.cap2:
            self.cap2.release()
