import pyttsx3


class TTS:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 125)
        self.engine.setProperty("volume", 1.0)
        self.set_polish_voice()
        self.engine.startLoop(False)

    def set_polish_voice(self):
        voices = self.engine.getProperty("voices")
        for voice in voices:
            voice_name = voice.name.lower()
            voice_id = voice.id.lower()
            if "polish" in voice_name or "pl" in voice_id:
                self.engine.setProperty("voice", voice.id)
                return
        print("Nie znaleziono polskiego głosu")

    def speak(self, phrase):
        self.engine.say(phrase)

    def process_audio(self, dt):
        
        try:
            self.engine.iterate()
        except TypeError:
            pass          

    def stop(self):
        self.engine.stop()