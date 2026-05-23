from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import partial

class PostawaKleczaca(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        btn = Button(text="Powrót",size_hint=(None,None),size=(200,50))
        btn.bind(on_press=partial(self.change_screen,'WzorowyPokaz'))
        self.add_widget(btn)

    def change_screen(self,target_screen,instance):
        self.manager.current = target_screen