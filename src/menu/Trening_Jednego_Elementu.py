from kivy.properties import partial
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button

class Trening_Jednego_Elementu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        btn = Button(text="Powrot do Menu",size_hint=(None,None), size=(200, 50))
        btn.bind(on_press=partial(self.change_screen, 'menu'))
        self.add_widget(btn)
    def change_screen(self, target_screen, instance):
        self.manager.current = target_screen