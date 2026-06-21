from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen,NoTransition
from kivy.app import App
from kivy.uix.image import Image

from ui.screens.kneeling_stance_screen import KneelingStanceScreen
from ui.screens.perfect_demo_screen import PerfectDemoScreen
from ui.screens.standing_stance_screen import StandingStanceScreen
from ui.screens.statistics_screen import StatisticsScreen
from ui.screens.supported_training_screen import *
from ui.screens.single_element_training_screen import *
from ui.components.hoverable_rounded_button import *
from vision.base_detection import *
from core.tts import *
from core.database_manager import *
import vision.excersises as ex

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
            source='ui/assets/lapka1.png',
            size_hint=(None, None),
            size=(100, 100),
            pos = (-100,-100)
        )
        #self.add_widget(self.cursor)
        self.detector_front = None
        self.cap = None
        self.update = None

    def change_screen(self, instance):
        target_screen = self.screen_mapping.get(instance.text)
        
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
        btn_kneel.bind(on_press=lambda x: self.start_training(target_screen_name, ex.KneelingStance(), popup)) 
        btn_cancel.bind(on_press=popup.dismiss)

        self.active_popup_buttons = [btn_stand, btn_kneel, btn_cancel]
        
        popup.bind(on_dismiss=lambda x: self.clear_popup_buttons())
        
        popup.open()
        if self.cursor in Window.children:
            Window.remove_widget(self.cursor)
        Window.add_widget(self.cursor)


    def start_training(self, target_screen_name, exercise_obj, popup):
        popup.dismiss()
        
        screen = self.manager.get_screen(target_screen_name)
        screen.screen_excersise = exercise_obj
        
        self.manager.current = target_screen_name

    def clear_popup_buttons(self):
        self.active_popup_buttons = []
        for button in self.menu_buttons:
            button.process_hover([]) 

    def on_enter(self):
        Window.add_widget(self.cursor)
        self.detector_front = self.manager.shared_detector_front
        Clock.schedule_once(self._late_camera_init, 0.2)

    def _late_camera_init(self, dt):
        self.cap = cv2.VideoCapture(1)
        if self.cap.isOpened():
            self.update = Clock.schedule_interval(self.update_frame, 1/30)
        else:
            print("Kamera nadal zablokowana przez system.")



    def on_leave(self):
        if self.cursor in Window.children:
            Window.remove_widget(self.cursor)
        if self.update:
            self.update.cancel()
            self.update = None
        if self.cap:
            self.cap.release()
            self.cap = None
        self.detector_front = None

        
        self.cursor.pos = (-100, -100)
        self.cursor.source = "ui/assets/lapka1.png"
        for button in self.menu_buttons:
            button.process_hover([])
 

    def update_frame(self, dt):
        if not self.cap or not self.cap.isOpened():
            return

        temp, frame = self.cap.read()
        if not temp:
            return
            
        frame = cv2.flip(frame, 1)
        _, result = self.detector_front.process_frame(frame)
        
        self.handle_cursor_and_hover()
                
    def handle_cursor_and_hover(self):
        if not self.detector_front:
            return

        if self.cursor.parent:
            if self.cursor.parent.children[0] != self.cursor:
                parent = self.cursor.parent
                parent.remove_widget(self.cursor)
                parent.add_widget(self.cursor)

        interaction_points = []
        for idx in [15, 17, 19, 16, 18, 20]:
            lm = self.detector_front.get_landmark_cords(idx)
            if lm:
                win_x = lm[0] * Window.width
                win_y = (1.0 - lm[1]) * Window.height
                interaction_points.append((win_x, win_y))

        # Wybieramy odpowiednią pulę przycisków
        current_buttons = self.active_popup_buttons if self.active_popup_buttons else self.menu_buttons

        if interaction_points:
            # aktualizacja pozycji kursora wizualnego
            main_lm = self.detector_front.get_landmark_cords(19)
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
                self.cursor.source = "ui/assets/lapka2.png"
            else:
                self.cursor.source = "ui/assets/lapka1.png"

        else:
            #brak ręki w kadrze
            self.cursor.pos = (-100, -100)
            self.cursor.source = "ui/assets/lapka1.png"
            for button in current_buttons:
                button.process_hover([])
                
                
                
                
class Menu(App):
    def build(self):
        Window.fullscreen = 'auto'
        sm = ScreenManager(transition=NoTransition())
        sm.shared_detector_front = BaseDetection()
        sm.shared_detector_side = BaseDetection()
        sm.shared_tts = TTS()
        sm.shared_db_manager = DatabaseManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SupportedTrainingScreen(screen_excersise=ex.StandingStance(), name='Trening wspierany'))
        sm.add_widget(SingleElementTrainingScreen(screen_excersise=ex.StandingStance(), name='TreningJednegoElementu'))
        sm.add_widget(PerfectDemoScreen(name='WzorowyPokaz'))
        sm.add_widget(StandingStanceScreen(name='PostawaStojaca'))
        sm.add_widget(KneelingStanceScreen(name='PostawaKleczaca'))
        sm.add_widget(StatisticsScreen(name='Statystyki'))
        return sm


if __name__ == '__main__':
    Menu().run()