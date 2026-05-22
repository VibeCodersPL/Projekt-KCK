import detection.excersises as ex
from kivy.core.image import Texture
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import cv2
from src.layout_api.TwoCameraFrameWindow import TwoCameraFrameWindow as TCFW
from src.layout_api.components.RoundedButton import *

class TreningWspierany(TCFW):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screenExcersise = ex.LowReady()

        self.is_training_started = False # Czy trening już się zaczął
        self.has_training_run = False  # Czy było start i potem stop (trening się zaczął i skończyć -> można go zapisać)
        self.is_training_saved = False  # Czy trening został już zapisany
        self.is_pose_correct = False

    def update_frame(self, dt):
        super().update_frame(dt)

        if self.is_training_started:
            #tutaj zwraca tuple (bool, bool) <- (czy jest dobrze wykonywana ta klatka, czy skonczył etap ćwiczenia)
            self.is_pose_correct, isStateEnded = self.screenExcersise.checkExcersise(self.landmarksFront, self.landmarksSide)
            if self.is_pose_correct:
                self.text_box.text = "DOBRZE!"
                self.text_box.color = (0.2, 1, 0.2, 1)  # Jasnozielony
            else:
                self.text_box.text = "SKORYGUJ POSTAWE"
                self.text_box.color = (1, 0.2, 0.2, 1)  # Czerwony
        else:
            self.is_pose_correct = False

            if self.is_training_saved:
                self.text_box.text = "TRENING ZAPISANY"
                self.text_box.color = (0.2, 0.6, 1, 1)  # Niebieski
            elif self.has_training_run:
                self.text_box.text = "ZAKONCZONO - ZAPISZ TRENING"
                self.text_box.color = (1, 0.8, 0, 1)  # Żółty
            else:
                self.text_box.text = "ROZPOCZNIJ CWICZENIE"
                self.text_box.color = (1, 1, 1, 1)  # Biały

    def on_base_start_click(self):
        """Metoda z klasy bazowej"""
        self.toggle_start_stop()

    def on_base_right_click(self):
        """Metodaz klasy bazowej"""
        can_save = self.has_training_run and not self.is_training_started and not self.is_training_saved
        if can_save:
            self.save_training()

    def toggle_start_stop(self):
        self.is_training_started = not self.is_training_started

        if self.is_training_started:
            print("Trening ROZPOCZĘTY")
            self.has_training_run = False
            self.is_training_saved = False
            self.btn_start.text = "STOP"
            self.btn_start.bg_color = (0.8, 0, 0, 1)
        else:
            print("Trening ZATRZYMANY")
            self.has_training_run = True
            self.btn_start.text = "START"
            self.btn_start.bg_color = (0, 0.7, 0, 1)

    def save_training(self):
        print("Trening ZAPISANY!")
        self.is_training_saved = True
        self.btn_save.text = "ZAPISANO"
        self.btn_save.bg_color = (0.6, 0, 0, 1)

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
        self.manager.current = target_screen