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
from Trening_Wspierany import *
from Wzorowy_Pokaz import *
from Wybor_Wzorca import *
from RoundedButton import *

POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # Ramiona
    (11, 23), (12, 24), (23, 24),  # Tułów
    (16, 18), (16, 22), (16, 20), (18, 20),  # prawa dlon
    (15, 21), (15, 19), (15, 17), (17, 19),  # lewa dlon
    (24, 26), (26, 28), (28, 30), (28, 32), (30, 32),  # prawa noga
    (23, 25), (25, 27), (27, 31), (27, 29), (31, 29)  # lewa noga
]


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        wid = Widget()
        layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(350, 320), spacing=20)
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
            'Trening jednego elementu': 'WyborWzorca',
            'Wzorowy pokaz': 'WzorowyPokaz'
        }
        for mode in self.screen_mapping.keys():
            button = RoundedButton(
                text=mode,
                font_size='18sp',
                color=(1, 1, 1, 1),
                bg_color=(0.15, 0.45, 0.85, 1),
                radius=30
            )
            button.bind(on_press=self.change_screen)
            layout.add_widget(button)
        root = AnchorLayout(anchor_x='center', anchor_y='center')
        root.add_widget(wid)
        root.add_widget(layout)
        self.add_widget(root)

    def change_screen(self, instance):
        target_screen = self.screen_mapping.get(instance.text)
        if target_screen:
            self.manager.current = target_screen

class Menu(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(TreningWspierany(name='Trening wspierany'))
        sm.add_widget(WyborWzorca(name='WyborWzorca'))
        sm.add_widget(WzorowyPokaz(name='WzorowyPokaz'))
        return sm


if __name__ == '__main__':
    Menu().run()