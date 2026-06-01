import pyttsx3
import threading

class TTS:
    def __init__(self):
        self.rate = 125
        self.volume = 1.0

    def _speak_task(self, phrase):
        """Prywatna funkcja wykonywana w tle. Na Linuksie najbezpieczniej 
        jest inicjować silnik i odpalać runAndWait() w tym samym wątku."""
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            
            # Ustawienie polskiego głosu
            voices = engine.getProperty("voices")
            for voice in voices:
                voice_name = voice.name.lower()
                voice_id = voice.id.lower()
                if "polish" in voice_name or "pl" in voice_id:
                    engine.setProperty("voice", voice.id)
                    break
                    
            engine.say(phrase)
            engine.runAndWait()
        except Exception as e:
            print(f"Błąd silnika TTS w tle: {e}")

    def set_polish_voice(self):
        pass

    def speak(self, phrase):
        threading.Thread(target=self._speak_task, args=(phrase,), daemon=True).start()
       

    def stop(self):
        pass