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
from kivy.uix.popup import Popup
from windows.Trening_Wspierany import *
from windows.Wzorowy_Pokaz import *
from windows.Trening_Jednego_Elementu import *
from layout_api.components.HoverableRoundedButton import *
from detection.base_detection import *
from windows.PostawaStojaca import *
from windows.PostawaKleczaca import *
from tts.tts import *
from database.database_manager import *
from windows.Statystyki import *
import detection.excersises as ex

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        wid = Widget()
        layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(350, 380), spacing=20)
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
            'Wzorowy pokaz': 'WzorowyPokaz',
            'Statystyki': 'Statystyki'
        }
        self.menu_buttons = []
        self.active_popup_buttons = []
        for mode in self.screen_mapping.keys():
            button = HoverableRoundedButton(
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
            source='./assets/lapka1.png',
            size_hint=(None, None),
            size=(100, 100),
            pos = (-100,-100)
        )
        self.add_widget(self.cursor)
        self.detector = None
        self.cap = None
        self.update = None

    def change_screen(self, instance):
        target_screen = self.screen_mapping.get(instance.text)
        
        # ZMIANA: Zamiast od razu przełączać ekran, sprawdzamy co zostało kliknięte
        if target_screen in ['Trening wspierany', 'TreningJednegoElementu']:
            self.show_exercise_popup(target_screen)
        elif target_screen:
            self.manager.current = target_screen

    def show_exercise_popup(self, target_screen_name):
        layout = BoxLayout(orientation='vertical', spacing=15, padding=15)

        btn_stand = HoverableRoundedButton(text='Postawa Stojąca', font_size='22sp', color=(1, 1, 1, 1), bg_color=(0.2, 0.6, 0.2, 1), radius=20)
        btn_kneel = HoverableRoundedButton(text='Postawa Klęcząca', font_size='22sp', color=(1, 1, 1, 1), bg_color=(0.2, 0.6, 0.2, 1), radius=20)
        btn_cancel = HoverableRoundedButton(text='Anuluj', font_size='22sp', color=(1, 1, 1, 1), bg_color=(0.8, 0.2, 0.2, 1), radius=20)

        layout.add_widget(btn_stand)
        layout.add_widget(btn_kneel)
        layout.add_widget(btn_cancel)

        popup = Popup(title='Wybierz ćwiczenie', content=layout, size_hint=(None, None), size=(400, 350))

        btn_stand.bind(on_press=lambda x: self.start_training(target_screen_name, ex.StandingStance(), popup))
        btn_kneel.bind(on_press=lambda x: self.start_training(target_screen_name, ex.StandingStance(), popup)) 
        btn_cancel.bind(on_press=popup.dismiss)

        self.active_popup_buttons = [btn_stand, btn_kneel, btn_cancel]
        
        popup.bind(on_dismiss=lambda x: self.clear_popup_buttons())
        
        popup.open()

    def start_training(self, target_screen_name, exercise_obj, popup):
        popup.dismiss()
        
        screen = self.manager.get_screen(target_screen_name)
        screen.screenExcersise = exercise_obj
        
        self.manager.current = target_screen_name

    def clear_popup_buttons(self):
        self.active_popup_buttons = []
        for button in self.menu_buttons:
            button.process_hover([]) # Wymuszamy reset podświetlenia menu głównego

    def on_enter(self):
        self.detector = self.manager.shared_detector
        Clock.schedule_once(self._late_camera_init, 0.2)

    def _late_camera_init(self, dt):
        self.cap = cv2.VideoCapture(1)
        if self.cap.isOpened():
            self.update = Clock.schedule_interval(self.update_frame, 1/30)
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

        
        self.cursor.pos = (-100, -100)
        self.cursor.source = "./assets/lapka1.png"
        for button in self.menu_buttons:
            button.process_hover([])
 


    def update_frame(self, dt):
        if not self.cap or not self.cap.isOpened():
            return

        temp, frame = self.cap.read()
        if not temp:
            return
            
        frame = cv2.flip(frame, 1)
        # Przetwarzamy klatkę dla detektora
        _, result = self.detector.process_frame(frame)
        
        self.handle_cursor_and_hover()
                
    def handle_cursor_and_hover(self):
        if not self.detector:
            return

        interaction_points = []
        for idx in [15, 17, 19, 16, 18, 20]:
            lm = self.detector.getLandmarkCords(idx)
            if lm:
                win_x = lm[0] * Window.width
                win_y = (1.0 - lm[1]) * Window.height
                interaction_points.append((win_x, win_y))

        # Wybieramy odpowiednią pulę przycisków
        current_buttons = self.active_popup_buttons if self.active_popup_buttons else self.menu_buttons

        if interaction_points:
            # aktualizacja pozycji kursora wizualnego
            main_lm = self.detector.getLandmarkCords(19)
            if main_lm:
                cursor_x = main_lm[0] * Window.width
                cursor_y = (1.0 - main_lm[1]) * Window.height
            else:
                cursor_x, cursor_y = interaction_points[0]

            self.cursor.pos = (cursor_x - self.cursor.width / 2, cursor_y - self.cursor.height / 2)

            #Obsługa najeżdżania na przyciski
            is_any_hovered = False
            for button in current_buttons:
                # Przekazujemy wszystkie punkty zebrane z dłoni
                button.process_hover(interaction_points)
                
                if any(button.collide_point(px, py) for px, py in interaction_points):
                    is_any_hovered = True

            if is_any_hovered:
                self.cursor.source = "./assets/lapka2.png"
            else:
                self.cursor.source = "./assets/lapka1.png"

        else:
            #brak ręki w kadrze
            self.cursor.pos = (-100, -100)
            self.cursor.source = "./assets/lapka1.png"
            for button in current_buttons:
                button.process_hover([])
                
                
                
                
class Menu(App):
    def build(self):
        Window.fullscreen = 'auto'
        sm = ScreenManager(transition=NoTransition())
        sm.shared_detector = BaseDetection()

        sm.shared_tts = TTS()
        sm.shared_db_manager = DatabaseManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(TreningWspierany(screenExcersise=ex.StandingStance(),name='Trening wspierany'))
        sm.add_widget(Trening_Jednego_Elementu(screenExcersise=ex.StandingStance(),name='TreningJednegoElementu'))
        sm.add_widget(WzorowyPokazScreen(name='WzorowyPokaz'))
        sm.add_widget(PostawaStojaca(name='PostawaStojaca'))
        sm.add_widget(PostawaKleczaca(name='PostawaKleczaca'))
        sm.add_widget(Statystyki(name='Statystyki'))
        return sm


if __name__ == '__main__':
    Menu().run()