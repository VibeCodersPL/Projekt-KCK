from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from ui.screens.two_camera_screen import TwoCameraScreen as TCFW
from ui.components.rounded_button import *
import vision.excersises as ex
from time import time

class SingleElementTrainingScreen(TCFW):
    def __init__(self, screen_excersise:ex.Exercise, **kwargs):
        super().__init__(screen_excersise=screen_excersise, **kwargs)
        
        self.tts = None 
        self.last_tts_message = 0
        self.tts_time = 4
        self.debug = False
        
        self.is_low_ready_active = True 

    def on_enter(self):
        super().on_enter()
        self.tts = self.manager.shared_tts
        
        if self.debug and self.screen_excersise:
            self.screen_excersise.start_excersise()
            self.screen_excersise.set_state("LowReady")
            self.is_low_ready_active = True

    def process_frame(self, frame, detector, landmarks, conditions, current_message):
        message = current_message
        
        for cond in conditions:
            if cond.condition_met:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
                if message is None and hasattr(cond, 'message'):
                    message = cond.message
            
            if self.debug and landmarks:
                angle = self.screen_excersise.calculate_three_point_angle(
                    landmarks[cond.landmarks[0]],
                    landmarks[cond.landmarks[1]],
                    landmarks[cond.landmarks[2]]
                )
                detector.print_deg_on_landmark(frame, cond.landmarks[1], angle)
            
            frame = detector.connect_landmarks(frame, cond.landmarks[0], cond.landmarks[1], color)
            frame = detector.connect_landmarks(frame, cond.landmarks[1], cond.landmarks[2], color)
            
        return frame, message

    def update_frame(self, dt):
        super().update_frame(dt, False)
        
        if self.front_frame is None or self.side_frame is None:
            return

        if self.screen_excersise and self.screen_excersise.is_running:
            if self.debug:
                print(self.screen_excersise.get_state_message())
            
            is_pose_correct, is_state_ended = self.screen_excersise.check_excersise(self.landmarks_front, self.landmarks_side)
            
            if self.debug:
                print(is_pose_correct, is_state_ended)
                
            if is_state_ended:
                if self.is_low_ready_active:
                    self.screen_excersise.set_state("LegsTorsoArms")
                    self.is_low_ready_active = False
                else:
                    self.screen_excersise.set_state("LowReady")
                    self.is_low_ready_active = True
                
                if self.debug:
                    print('zmieniam stan')
                    print(self.screen_excersise.get_state_message())
                    print(self.screen_excersise.get_end_stats())

            message = None
                    
            if self.landmarks_front and self.landmarks_side:
                cond_front, cond_side = self.screen_excersise.get_state_conditions()
                
                # --- PRZETWARZANIE KAMERY PRZEDNIEJ ---
                self.front_frame, message = self.process_frame(
                    self.front_frame,
                    self.detector_front, 
                    self.landmarks_front,
                    cond_front, 
                    message
                )
                
                # --- PRZETWARZANIE KAMERY BOCZNEJ ---
                self.side_frame, message = self.process_frame(
                    self.side_frame,
                    self.detector_side, 
                    self.landmarks_side,
                    cond_side, 
                    message
                )
                
                if is_pose_correct:
                    self.set_title_text("DOBRZE!", (0.2, 1, 0.2, 1))
                else:
                    self.set_title_text("SKORYGUJ POSTAWE", (1, 0.2, 0.2, 1))

                    current_time = time()
                    if message and (current_time - self.last_tts_message) >= self.tts_time:
                        if self.tts:
                            self.tts.speak(message)
                        self.last_tts_message = current_time
            else:
                self.text_box.text = "STAŃ W ZASIĘGU KAMER"
            
        else:
            if self.screen_excersise and self.screen_excersise.is_saved:
                self.set_title_text("TRENING ZAPISANY", (0.2, 0.6, 1, 1))
            elif self.screen_excersise and self.screen_excersise.has_run:
                self.set_title_text("ZAKONCZONO - ZAPISZ TRENING", (1, 0.8, 0, 1))
            else:
                self.set_title_text("ROZPOCZNIJ CWICZENIE")

        if self.front_frame is not None:
            self.camera_view.texture = self.frame_to_texture(self.front_frame)
        if self.side_frame is not None:
            self.camera_view2.texture = self.frame_to_texture(self.side_frame)

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
            font_size='24sp'
        )
        msg_label.bind(size=msg_label.setter('text_size'))

        buttons_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.3)

        btn_yes = RoundedButton(
            text="Tak",
            font_size='26sp',
            color=(1, 1, 1, 1),
            bg_color=(0.15, 0.45, 0.85, 1),
            radius=45
        )
        btn_no = RoundedButton(
            text="Nie",
            font_size='26sp',
            color=(1, 1, 1, 1),
            bg_color=(0.15, 0.45, 0.85, 1),
            radius=45
        )

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
        if self.screen_excersise:
            self.screen_excersise.is_running = False
        self.manager.current = target_screen
        
    def on_base_save_click(self, training_type_int:int = 0):
        return super().on_base_save_click(1)