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
from layout_api.components.RoundedButton import RoundedButton
from layout_api.components.HoverableRoundedButton import HoverableRoundedButton

import detection.excersises as Ex
import detection.base_detection as Bd
import database.database_manager as DBM

class TwoCameraFrameWindow(Screen):
    screenExcersise: Ex.Exercise = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.detector_front = None
        self.detector_side = None

        self.landmarksFront = []
        self.landmarksSide = []
        
        # ZABEZPIECZENIE: Zmienne zainicjowane z góry
        self.frontFrame = None
        self.sideFrame = None
        self.cap = None
        self.cap2 = None
        self.update_event = None

        self.main_layout = FloatLayout()

        self.cameras_layout = BoxLayout(orientation="horizontal", spacing=15, size_hint=(1, 0.8),
                                        pos_hint={'center_y': 0.45})
        self.camera_view = Image(size_hint=(1, 1), allow_stretch=True)
        self.camera_view2 = Image(size_hint=(1, 1), allow_stretch=True)
        self.cameras_layout.add_widget(self.camera_view)
        self.cameras_layout.add_widget(self.camera_view2)

        self.ui_layer = FloatLayout()

        btn = RoundedButton(
            text="Powrót do menu",
            font_size='16sp',
            bg_color=(0.15, 0.45, 0.85, 1),
            radius=30,
            size_hint=(0.1, 0.07),
            pos_hint={'center_x': 0.5, 'y': 0.0}
        )
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
        self.btn_start = HoverableRoundedButton(
            text="START",
            font_size='24sp',
            bg_color=(0, 0.7, 0, 1),
            radius=30,
            hover_threshold=30,
            size_hint=(0.1, 0.07),
            pos_hint={'x': 0.02, 'y': 0.65}
        )
        self.btn_start.bind(on_release=lambda x: self.on_base_start_click())

        self.btn_save = HoverableRoundedButton(
            text="ZAPISZ",
            font_size='24sp',
            bg_color=(0.4, 0.4, 0.4, 1),
            radius=30,
            hover_threshold=30,
            size_hint=(0.1, 0.07),
            pos_hint={'x': 0.38, 'y': 0.65}
        )
        self.btn_save.bind(on_release=lambda x: self.on_base_save_click())

        self.ui_layer.add_widget(self.btn_start)
        self.ui_layer.add_widget(self.btn_save)

    def handle_base_hover(self):
        """Logika najeżdżania na bazowe przyciski z powiększonym marginesem błędu i płynnym cofaniem"""
        if not self.detector_front:
            return

        wrists = []
        for idx in [15, 17, 19, 16, 18, 20]:
            lm = self.detector_front.getLandmarkCords(idx)
            if lm:
                kivy_x = self.camera_view.x + (lm[0] * self.camera_view.width)
                kivy_y = self.camera_view.y + ((1.0 - lm[1]) * self.camera_view.height)
                wrists.append((kivy_x, kivy_y))

        if self.screenExcersise:
            self.btn_save.is_hover_active = (self.screenExcersise.has_run and 
                                             not self.screenExcersise.is_running and 
                                             not self.screenExcersise.is_saved)
            
        if hasattr(self, 'btn_start'):
            self.btn_start.process_hover(wrists)
            
        if hasattr(self, 'btn_save'):
            self.btn_save.process_hover(wrists)

    def on_base_start_click(self):
        if not self.screenExcersise: return

        is_now_running = self.screenExcersise.toggle_running()

        if is_now_running:
            print("Trening ROZPOCZĘTY!")
            self.btn_start.text = "STOP"
            self.btn_start.bg_color = (0.8, 0, 0, 1)
        else:
            print("Trening ZATRZYMANY!")
            self.btn_start.text = "START"
            self.btn_start.bg_color = (0, 0.7, 0, 1)

    def on_base_save_click(self, training_type_int:int = 0):
        if not self.screenExcersise: return
        
        can_save = self.screenExcersise.has_run and not self.screenExcersise.is_running and not self.screenExcersise.is_saved
        
        if can_save:
            print("Trening ZAPISANY!")
            self.screenExcersise.mark_as_saved() 
            self.btn_save.text = "ZAPISANO"
            self.btn_save.bg_color = (0.6, 0, 0, 1)
            
            from datetime import datetime
            import time
            
            current_time = datetime.now()
            end_time_str = current_time.strftime("%H:%M:%S")
            
            start_timestamp = getattr(self.screenExcersise, '_timeOfExcersiseStart', time.time())
            start_time_obj = datetime.fromtimestamp(start_timestamp)
            start_time_str = start_time_obj.strftime("%H:%M:%S")
            nazwa = self.screenExcersise._excersiseName
            stats = self.screenExcersise.getEndStats()
            
            try:
                trening_id = self.databaseManager.save_training(training_type_int, start_time_str, end_time_str, nazwa, stats)
                print(f"Pomyślnie wstawiono rekord. ID Treningu: {trening_id}")
            except Exception as e:
                print(f"Błąd podczas zapisu do bazy danych: {e}")

    def set_title_text(self, text, color=(1, 1, 1, 1)):
        self.text_box.text = text
        self.text_box.color = color

    def change_screen(self, target_screen, instance):
        self.manager.current = target_screen

    def on_enter(self):
        self.detector_front = self.manager.shared_detector_front
        self.detector_side = self.manager.shared_detector_side

        self.databaseManager:DBM.DatabaseManager = self.manager.shared_db_manager
        Clock.schedule_once(self._late_camera_init, 0.2)

    def _late_camera_init(self, dt):
        self.cap = cv2.VideoCapture(1)
        
        self.cap2 = cv2.VideoCapture(0)
        
        if(not self.cap2 or not self.cap2.isOpened()):
           self.cap2 = self.cap 

        if self.cap.isOpened() or self.cap2.isOpened():
            self.update_event = Clock.schedule_interval(self.update_frame, 1/30)
        else:
            print("Kamera zablokowana przez system lub niedostępna.")

    def update_frame(self, dt, toTexture: bool = True):
        if (not self.cap or not self.cap.isOpened()) and (not self.cap2 or not self.cap2.isOpened()):
            return

        self.handle_base_hover()

        if self.cap and self.cap.isOpened():
            self.frontFrame, self.landmarksFront = self.update_camera(self.cap, self.detector_front)
            if toTexture and self.frontFrame is not None:
                self.camera_view.texture = self.frameToTexture(self.frontFrame)

        if self.cap2 and self.cap2.isOpened():
            self.sideFrame, self.landmarksSide = self.update_camera(self.cap2, self.detector_side)
            if toTexture and self.sideFrame is not None:
                self.camera_view2.texture = self.frameToTexture(self.sideFrame)

    def update_camera(self, cap, detector):
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            processed_frame, result = detector.process_frame(frame)
            landmarks = detector.getLandmarks()
            return processed_frame, landmarks
        # ZABEZPIECZENIE: Zwraca poprawnie pusty zestaw w razie błędu kamery
        return None, []

    def frameToTexture(self,frame):
        if frame is None:
            return None
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