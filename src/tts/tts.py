import pyttsx3
import threading
import queue

class TTS:
    def __init__(self):
        self.rate = 125
        self.volume = 1.0
        self.message_queue = queue.Queue()
        self.thread = threading.Thread(target=self._speak_task, daemon=True)
        self.thread.start()

    def set_polish_voice(self, engine):
        try:
            voices = engine.getProperty("voices")
            for voice in voices:
                voice_name = voice.name.lower()
                voice_id = voice.id.lower()
                if "polish" in voice_name or "pl" in voice_id:
                    engine.setProperty("voice", voice.id)
                    print(f"[TTS] Ustawiono głos: {voice.name}")
                    return
            print("[TTS] Nie znaleziono polskiego głosu. Używam domyślnego.")
        except Exception as e:
            print(f"[TTS] Błąd podczas ustawiania głosu: {e}")

    def _speak_task(self):
        """Prywatna funkcja wykonywana w tle."""
        try:
            print("[TTS] Inicjalizacja silnika pyttsx3 w tle...")
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            self.set_polish_voice(engine)
            print("[TTS] Silnik gotowy do pracy.")

            while True:
                phrase = self.message_queue.get()
                if phrase is None:
                    print("[TTS] Zamykanie wątku TTS.")
                    break

                print(f"[TTS] Mówię: {phrase}")
                engine.say(phrase)
                engine.runAndWait()
                self.message_queue.task_done()
                print("[TTS] Zakończono mówienie.")

        except Exception as e:
            print(f"[TTS] Krytyczny błąd silnika TTS w tle: {e}")

    def speak(self, phrase):
        """Dodaje frazę do kolejki, jeśli nie jest przepełniona."""
        if self.message_queue.qsize() < 2:
            self.message_queue.put(phrase)

    def stop(self):
        self.message_queue.put(None)