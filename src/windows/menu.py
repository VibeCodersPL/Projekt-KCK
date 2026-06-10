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


    def on_enter(self):
        self.detector = self.manager.shared_detector_front
        Clock.schedule_once(self._late_camera_init, 0.2)

    def _late_camera_init(self, dt):
        self.cap = cv2.VideoCapture(0)
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
        _, result = self.detector.process_frame(frame)
        cursor_pos = self.detector.getLandmarkCords(19)

        if cursor_pos is not None:
            x, y = cursor_pos
            win_x = x * Window.width
            win_y = (1 - y) * Window.height
            self.cursor.pos = (win_x - self.cursor.width / 2, win_y - self.cursor.height / 2)
            
            is_any_hovered = False
            point = [(win_x, win_y)]

            for button in self.menu_buttons:
                # przekazujemy punkt do przycisku
                button.process_hover(point)
                
                # sprawdzamy, czy musimy zmienić ikonę łapki
                if button.collide_point(win_x, win_y):
                    is_any_hovered = True

            # Aktualizacja wyglądu kursora
            if is_any_hovered:
                self.cursor.source = "./assets/lapka2.png"
            else:
                self.cursor.source = "./assets/lapka1.png"
                
        else:
            # ręka zniknęła z kamery: chowamy kursor i informujemy przyciski, by wycofały paski
            self.cursor.pos = (-100, -100)
            self.cursor.source = "./assets/lapka1.png"
            for button in self.menu_buttons:
                button.process_hover([])
                
    def change_screen(self, instance):
        target_screen = self.screen_mapping.get(instance.text)
        if target_screen:
            self.manager.current = target_screen
                
class Menu(App):
    def build(self):
        Window.fullscreen = 'auto'
        sm = ScreenManager(transition=NoTransition())
        sm.shared_detector_front = BaseDetection()
        sm.shared_tts = TTS()
        sm.shared_db_manager = DatabaseManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(TreningWspierany(name='Trening wspierany'))
        sm.add_widget(Trening_Jednego_Elementu(name='TreningJednegoElementu'))
        sm.add_widget(WzorowyPokazScreen(name='WzorowyPokaz'))
        sm.add_widget(PostawaStojaca(name='PostawaStojaca'))
        sm.add_widget(PostawaKleczaca(name='PostawaKleczaca'))
        sm.add_widget(Statystyki(name='Statystyki'))
        return sm


if __name__ == '__main__':
    Menu().run()