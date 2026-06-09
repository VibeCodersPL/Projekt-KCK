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
        # Ustawienie polskiego głosu
        voices = engine.getProperty("voices")
        for voice in voices:
            voice_name = voice.name.lower()
            voice_id = voice.id.lower()
            if "polish" in voice_name or "pl" in voice_id:
                engine.setProperty("voice", voice.id)
                break

    def _speak_task(self):
        """Prywatna funkcja wykonywana w tle. Na Linuksie najbezpieczniej
        jest inicjować silnik i odpalać runAndWait() w tym samym wątku."""
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            self.set_polish_voice(engine)

            while True:
                phrase = self.message_queue.get()
                if phrase is None:
                    break

                engine.say(phrase)
                engine.runAndWait()
                self.message_queue.task_done()

        except Exception as e:
            print(f"Błąd silnika TTS w tle: {e}")


    def speak(self, phrase):
        self.message_queue.put(phrase)


    def stop(self):
        self.message_queue.put(None)