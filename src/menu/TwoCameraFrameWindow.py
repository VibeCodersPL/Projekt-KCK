from kivy.properties import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2



class TwoCameraFrameWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        btn = Button(text="Powrot do Menu",size_hint=(None,None), size=(200, 50))
        btn.bind(on_press=partial(self.change_screen, 'menu'))
        cameras_layout = BoxLayout(orientation = "horizontal", spacing=15, size_hint=(1,0.8))
        
        self.camera_view = Image(size_hint=(1, 0.5), pos_hint={'center_x': 0.25, 'center_y': 0.5})
        self.camera_view2 = Image(size_hint=(1, 0.5), pos_hint={'center_x': 0.25, 'center_y': 0.5})

        cameras_layout.add_widget(self.camera_view)
        cameras_layout.add_widget(self.camera_view2)

        
        self.add_widget(btn)
        self.add_widget(cameras_layout)
        
        
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
                self.camera_view.texture = self.update_camera(self.cap)
                
            if(self.cap2.isOpened()):
                self.camera_view2.texture = self.update_camera(self.cap2, True)


    def update_camera(self, cap, isSide:bool = False):

        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)

            processed_frame, result = self.detector.process_frame(frame)

            if (self.detector.checkExcersise(self.screenExcersise, isSide) == False):
                print("niepoprawnie wykonywane cwiczenie")
            else:
                print("super ci idzie")

            buf = cv2.flip(processed_frame, 0).tobytes()

            # 2. Utworzenie tekstury (wymiary z klatki)
            texture = Texture.create(
                size=(processed_frame.shape[1], processed_frame.shape[0]),
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
