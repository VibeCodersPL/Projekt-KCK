import pyttsx3
import threading
import queue
import platform

class TTS:
    def __init__(self):
        self.rate = 125
        self.volume = 1.0
        self.message_queue = queue.Queue()
        self.is_speaking = False
        self.thread = threading.Thread(target=self._speak_task, daemon=True)
        self.thread.start()

    def _speak_task(self):
        """Prywatna funkcja wykonywana w tle."""
        print("[TTS] Wątek startuje.", flush=True)

        if platform.system() == 'Windows':
            try:
                import comtypes
                comtypes.CoInitialize()
            except Exception as e:
                print(f"[TTS] Ostrzeżenie COM: {e}", flush=True)

        while True:
            phrase = self.message_queue.get()
            if phrase is None:
                print("[TTS] Zamykanie wątku TTS.", flush=True)
                break

            self.is_speaking = True
            print(f"[TTS] Mówię: {phrase}", flush=True)
            
            try:
                # INIT W ŚRODKU PĘTLI - zapobiega zamrożeniom i crashom na Windowsie
                engine = pyttsx3.init()
                engine.setProperty("rate", self.rate)
                engine.setProperty("volume", self.volume)

                # Ustawianie polskiego głosu
                voices = engine.getProperty("voices")
                for voice in voices:
                    if "polish" in voice.name.lower() or "pl" in voice.id.lower():
                        engine.setProperty("voice", voice.id)
                        break
                
                engine.say(phrase)
                engine.runAndWait()
                
                # Usunięcie instancji po wypowiedzi zwalnia obiekty COM
                del engine 
                
            except Exception as e:
                print(f"[TTS] Błąd podczas mówienia (runAndWait): {e}", flush=True)
            finally:
                self.is_speaking = False
                self.message_queue.task_done()
                print("[TTS] Zakończono frazę.", flush=True)

    def speak(self, phrase):
        """Dodaje frazę do kolejki tylko, jeśli bot obecnie milczy i kolejka jest pusta."""
        print(f"[TTS] Próba dodania do kolejki: {phrase}", flush=True)
        if not self.is_speaking and self.message_queue.empty():
            self.message_queue.put(phrase)

    def stop(self):
        self.message_queue.put(None)