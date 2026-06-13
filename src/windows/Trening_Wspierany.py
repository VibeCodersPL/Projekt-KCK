from typing import List

from kivy.core.image import Texture
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from layout_api.TwoCameraFrameWindow import TwoCameraFrameWindow as TCFW
from layout_api.components.RoundedButton import *
import detection.excersises as ex
from tts.tts import TTS
from time import time

class TreningWspierany(TCFW):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screenExcersise = ex.StandingStance()
        
        self.tts = None 
        self.last_tts_message = 0
        self.tts_time = 4
        
        self.debug = True
        if self.debug:
            self.screenExcersise.start_excersise()

    def on_enter(self):
        super().on_enter()
        self.tts = self.manager.shared_tts

    def update_frame(self, dt):
        super().update_frame(dt, False)
        
        if self.frontFrame is None or self.sideFrame is None:
            return

        if self.screenExcersise and self.screenExcersise.is_running:
            if self.debug:
                print(self.screenExcersise.getStateMessage())
            
            is_pose_correct, isStateEnded = self.screenExcersise.checkExcersise(self.landmarksFront, self.landmarksSide)            
            if self.debug:
                print(is_pose_correct, isStateEnded)
            if isStateEnded:
                if self.debug:
                    #self.screenExcersise.setState(None)
                    print('zmieniam stan')
                    print(self.screenExcersise.getStateMessage())
                    print(self.screenExcersise.getEndStats())

            message = None
                    
            # Rysowanie na kamerze przedniej
            condFront, condSide = self.screenExcersise.getStateConditions()
            for cond in condFront:
                if cond.conditionMet:
                    color = (0,255,0)
                else:
                    color = (0,0,255)
                    if message is None and hasattr(cond,'message'):
                        message = cond.message
                if self.debug:               
                    if self.landmarksFront:
                        self.detector_front.printDegOnLandmark(self.frontFrame,cond.landmarks[1], self.screenExcersise.calculateThreePointAngle(self.landmarksFront[cond.landmarks[0]],self.landmarksFront[cond.landmarks[1]],self.landmarksFront[cond.landmarks[2]]))
                self.frontFrame = self.detector_front.connectLandmarks(self.frontFrame,cond.landmarks[0],cond.landmarks[1],color)
                self.frontFrame = self.detector_front.connectLandmarks(self.frontFrame,cond.landmarks[1],cond.landmarks[2],color)
                    
            # Rysowanie na kamerze bocznej
            for cond in condSide:
                if cond.conditionMet:
                    color = (0,255,0)
                else:
                    color = (0,0,255)
                    if message is None and hasattr(cond,'message'):
                        message = cond.message
                if self.debug:
                    if self.landmarksSide:
                        self.detector_side.printDegOnLandmark(self.sideFrame,cond.landmarks[1], self.screenExcersise.calculateThreePointAngle(self.landmarksSide[cond.landmarks[0]],self.landmarksSide[cond.landmarks[1]],self.landmarksSide[cond.landmarks[2]]))        
                self.sideFrame = self.detector_side.connectLandmarks(self.sideFrame,cond.landmarks[0],cond.landmarks[1],color)
                self.sideFrame = self.detector_side.connectLandmarks(self.sideFrame,cond.landmarks[1],cond.landmarks[2],color)

            if is_pose_correct:
                self.text_box.text = "DOBRZE!"
                self.text_box.color = (0.2, 1, 0.2, 1)  # Jasnozielony
            else:
                self.text_box.text = "SKORYGUJ POSTAWE"
                self.text_box.color = (1, 0.2, 0.2, 1)  # Czerwony

                current_time = time()
                if message and (current_time - self.last_tts_message) >= self.tts_time:
                    if self.tts:
                        self.tts.speak(message)
                    self.last_tts_message = current_time
        
        else:
            if self.screenExcersise and self.screenExcersise.is_saved:
                self.text_box.text = "TRENING ZAPISANY"
                self.text_box.color = (0.2, 0.6, 1, 1)  # Niebieski
            elif self.screenExcersise and self.screenExcersise.has_run:
                self.text_box.text = "ZAKONCZONO - ZAPISZ TRENING"
                self.text_box.color = (1, 0.8, 0, 1)  # Żółty
            else:
                self.text_box.text = "ROZPOCZNIJ CWICZENIE"
                self.text_box.color = (1, 1, 1, 1)  # Biały
        
        self.camera_view.texture = self.frameToTexture(self.frontFrame)
        self.camera_view2.texture = self.frameToTexture(self.sideFrame)                

    def change_screen(self, target_screen, instance):
        if target_screen == 'menu':
            self.show_exit_confirmation(target_screen)
        else:
            super().change_screen(target_screen, instance)

    def show_exit_confirmation(self, target_screen):
        content_layout = BoxLayout(orientation='vertical', spacing=20, padding=20)

        msg_label = Label(
            text="Czy chcesz przerwać trening i wyjść?",
            size_hint_y=0.7,
            halign='center',
            valign='middle',
            font_size = '24sp'
        )
        msg_label.bind(size=msg_label.setter('text_size'))

        buttons_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.3)

        btn_yes = RoundedButton(text="Tak",
                    font_size='26sp',
                    color=(1, 1, 1, 1),
                    bg_color=(0.15, 0.45, 0.85, 1),
                    radius=45)
        btn_no = RoundedButton(text="Nie",
                    font_size='26sp',
                    color=(1, 1, 1, 1),
                    bg_color=(0.15, 0.45, 0.85, 1),
                    radius=45)

        buttons_layout.add_widget(btn_yes)
        buttons_layout.add_widget(btn_no)

        content_layout.add_widget(msg_label)
        content_layout.add_widget(buttons_layout)

        self.exit_popup = Popup(
            title='Przerwanie treningu',
            content=content_layout,
            size_hint=(0.4, 0.4),
            auto_dismiss=False
        )

        btn_yes.bind(on_press=lambda inst: self.confirm_exit(target_screen))
        btn_no.bind(on_press=self.exit_popup.dismiss)

        self.exit_popup.open()

    def confirm_exit(self, target_screen):
        self.exit_popup.dismiss()
        print("Trening przerwany. Ćwiczenie nie zostało zapisane.")
        if self.screenExcersise:
            self.screenExcersise.is_running = False
        self.manager.current = target_screen
        
    def on_base_save_click(self, training_type_int:int = 0):
        return super().on_base_save_click(1)