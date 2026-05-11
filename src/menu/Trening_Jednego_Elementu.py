from kivy.properties import partial
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2




class Trening_Jednego_Elementu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        
        btn = Button(text="Powrot do Menu",size_hint=(None,None), size=(200, 50))
        btn.bind(on_press=partial(self.change_screen, 'menu'))
        
        
        self.camera_view = Image(size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.camera_view)        
        
        
        self.add_widget(btn)
        
        
    def change_screen(self, target_screen, instance):
        self.manager.current = target_screen
        
    def on_enter(self):
        self.detector = self.manager.shared_detector
        Clock.schedule_once(self._late_camera_init, 0.2)

    def _late_camera_init(self, dt):
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            self.update_event = Clock.schedule_interval(self.update_frame, 1/30)
        else:
            print("Kamera nadal zablokowana przez system.")
            
    def update_frame(self, dt):
            if not self.cap or not self.cap.isOpened():
                return

            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                
                processed_frame, result = self.detector.process_frame(frame)
                

                buf = cv2.flip(processed_frame, 0).tobytes()
                
                # 2. Utworzenie tekstury (wymiary z klatki)
                texture = Texture.create(
                    size=(processed_frame.shape[1], processed_frame.shape[0]), 
                    colorfmt='bgr'
                )
                
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                
                self.camera_view.texture = texture
            
    def on_leave(self):
        """Uruchamiane przy wychodzeniu - zwalnianie zasobów"""
        if self.update_event:
            self.update_event.cancel()
        if self.cap:
            self.cap.release()
