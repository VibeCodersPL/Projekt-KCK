import json
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import partial
from src.tts.tts import *
from pathlib import Path

class PostawaKleczaca(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tts = TTS()
        self.speak_event = None
        JSON_PATH = Path(__file__).resolve().parents[1] / "tts" / "phrases.json"
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            self.phrases = json.load(f)
        btn = Button(text="Powrót",size_hint=(None,None),size=(200,50))
        btn.bind(on_press=partial(self.change_screen,'WzorowyPokaz'))
        self.add_widget(btn)

    def on_enter(self, *args):
        self.speak_event = Clock.schedule_once(self.speak_phrases, 3)

    def speak_phrases(self, dt):
        for phrase in self.phrases["WzorowyPokazKleczaca"]:
            self.tts.speak(phrase)

    def on_leave(self, *args):
        if self.speak_event:
            self.speak_event.cancel()

    def change_screen(self,target_screen,instance):
        self.manager.current = target_screen

