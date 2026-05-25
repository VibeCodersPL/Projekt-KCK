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
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from src.layout_api.components.RoundedButton import RoundedButton
import src.detection.excersises as Ex
import src.detection.base_detection as Bd

class TwoCameraFrameWindow(Screen):
    screenExcersise: Ex.Exercise = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.landmarksFront = None
        self.landmarksSide = None

        self.hover_start_frames = 0
        self.hover_rest_frames = 0
        self.HOVER_THRESHOLD = 30

        self.is_training_started = False  # Czy trening już się zaczął
        self.has_training_run = False  # Czy było start i potem stop (trening się zaczął i skończyć -> można go zapisać)
        self.is_training_saved = False  # Czy trening został już zapisany

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
            size_hint=(0.1, 0.07),
            pos_hint={'x': 0.02, 'y': 0.65}
        )
        with self.btn_start.canvas.after:
            self.start_color = Color(0, 1, 0, 0)
            self.start_rect = RoundedRectangle(pos=self.btn_start.pos, size=(0, 0), radius=[10])

        self.btn_save = RoundedButton(
            text="ZAPISZ",
            font_size='24sp',
            bg_color=(0.4, 0.4, 0.4, 1),
            radius=10,
            size_hint=(0.1, 0.07),
            pos_hint={'x': 0.38, 'y': 0.65}
        )
        with self.btn_save.canvas.after:
            self.save_color = Color(0, 1, 0, 0)
            self.save_rect = RoundedRectangle(pos=self.btn_save.pos, size=(0, 0), radius=[10])

        self.add_ui_element(self.btn_start)
        self.add_ui_element(self.btn_save)

    def handle_base_hover(self):
        """Logika najeżdżania na bazowe przyciski z powiększonym marginesem błędu i płynnym cofaniem"""
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
        right_hovered = False

        # Margines Błędu
        MARGIN = 60

        can_save = self.has_training_run and not self.is_training_started and not self.is_training_saved

        for x, y in wrists:
            if hasattr(self, 'btn_start'):
                b = self.btn_start
                if (b.x - MARGIN <= x <= b.right + MARGIN) and (b.y - MARGIN <= y <= b.top + MARGIN):
                    start_hovered = True

            if hasattr(self, 'btn_save') and can_save:
                b = self.btn_save
                if (b.x - MARGIN <= x <= b.right + MARGIN) and (b.y - MARGIN <= y <= b.top + MARGIN):
                    right_hovered = True

        # --- LOGIKA START ---
        if start_hovered:
            if self.hover_start_frames >= 0:
                self.hover_start_frames += 1
                if self.hover_start_frames >= self.HOVER_THRESHOLD:
                    self.on_base_start_click()
                    self.hover_start_frames = -30
        else:
            if self.hover_start_frames > 0:
                self.hover_start_frames -= 1

        if self.hover_start_frames < 0:
            self.hover_start_frames += 1

        # --- LOGIKA ZAPISZ ---
        if right_hovered:
            if self.hover_rest_frames >= 0:
                self.hover_rest_frames += 1
                if self.hover_rest_frames >= self.HOVER_THRESHOLD:
                    self.on_base_save_click()
                    self.hover_rest_frames = -30
        else:
            if self.hover_rest_frames > 0:
                self.hover_rest_frames -= 1

        if self.hover_rest_frames < 0:
            self.hover_rest_frames += 1

        # --- AKTUALIZACJA PASKÓW ---
        start_progress = max(0, self.hover_start_frames) / self.HOVER_THRESHOLD
        right_progress = max(0, self.hover_rest_frames) / self.HOVER_THRESHOLD

        if hasattr(self, 'start_rect'):
            self.start_rect.pos = self.btn_start.pos
            self.start_rect.size = (self.btn_start.width * start_progress, self.btn_start.height)
            self.start_color.a = 0.5 if start_progress > 0 else 0

        if hasattr(self, 'save_rect'):
            self.save_rect.pos = self.btn_save.pos
            self.save_rect.size = (self.btn_save.width * right_progress, self.btn_save.height)
            self.save_color.a = 0.5 if right_progress > 0 else 0

    # --- Metody do nadpisywania w klasach dziedziczących ---
    def on_base_start_click(self):
        self.is_training_started = not self.is_training_started

        if self.is_training_started:
            print("Trening ROZPOCZĘTY!)")
            self.has_training_run = False
            self.is_training_saved = False
            self.btn_start.text = "STOP"
            self.btn_start.bg_color = (0.8, 0, 0, 1)
        else:
            print("Trening ZATRZYMANY!")
            self.has_training_run = True
            self.btn_start.text = "START"
            self.btn_start.bg_color = (0, 0.7, 0, 1)

    def on_base_save_click(self):
        can_save = self.has_training_run and not self.is_training_started and not self.is_training_saved
        if can_save:
            print("Trening ZAPISANY!")
            self.is_training_saved = True
            self.btn_save.text = "ZAPISANO"
            self.btn_save.bg_color = (0.6, 0, 0, 1)

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
        self.detector:Bd.BaseDetection = self.manager.shared_detector
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

    def update_frame(self, dt, toTexture:bool = True):
            if not self.cap or not self.cap.isOpened() and not self.cap2 or not self.cap2.isOpened():
                return

            self.handle_base_hover()

            if(self.cap.isOpened()):
                self.frontFrame, self.landmarksFront = self.update_camera(self.cap)
                if(toTexture):
                    self.camera_view.texture = self.frameToTexture(self.frontFrame)
                
                
                
            if(self.cap2.isOpened()):
                self.sideFrame, self.landmarksFront = self.update_camera(self.cap2)
                if(toTexture):
                    self.camera_view2.texture = self.frameToTexture(self.sideFrame)
                
                

                
                

    def update_camera(self, cap):
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)

            processed_frame, result = self.detector.process_frame(frame, connecting=True)
            landmarks = self.detector.getLandmarks()

  

            return processed_frame, landmarks


    def frameToTexture(self,frame):
            buf = cv2.flip(frame, 0).tobytes()

            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]),
                colorfmt='bgr'
            )

            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            return texture

    def on_leave(self):
        """Uruchamiane przy wychodzeniu - zwalnianie zasobów"""
        if self.update_event:
            self.update_event.cancel()
        if self.cap:
            self.cap.release()
        if self.cap2:
            self.cap2.release()
