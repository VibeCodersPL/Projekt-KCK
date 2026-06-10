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

    def _speak_task(self):
        """Prywatna funkcja wykonywana w tle."""
        print("[TTS] Wątek TTS gotowy do pracy w tle.", flush=True)

        while True:
            phrase = self.message_queue.get()
            if phrase is None:
                print("[TTS] Zamykanie wątku TTS.", flush=True)
                break

            print(f"[TTS] Mówię: {phrase}", flush=True)
            try:
                # Trik dla Windowsa: inicjalizujemy silnik od nowa dla 
                # każdej frazy. Zapobiega to blokowaniu się pętli SAPI5.
                engine = pyttsx3.init()
                engine.setProperty("rate", self.rate)
                engine.setProperty("volume", self.volume)

                # Ustawienie polskiego głosu
                voices = engine.getProperty("voices")
                for voice in voices:
                    name = voice.name.lower()
                    vid = voice.id.lower()
                    if "polish" in name or "pl" in vid:
                        engine.setProperty("voice", voice.id)
                        break

                engine.say(phrase)
                engine.runAndWait()
                
                # Bezpieczne usunięcie silnika z pamięci (ważne dla Windowsa)
                del engine 

            except Exception as e:
                print(f"[TTS] Krytyczny błąd silnika TTS: {e}", flush=True)
            finally:
                self.message_queue.task_done()
                print("[TTS] Zakończono mówienie.", flush=True)

    def speak(self, phrase):
        """Dodaje frazę do kolejki, jeśli nie jest przepełniona (anti-spam)."""
        if self.message_queue.qsize() < 2:
            self.message_queue.put(phrase)

    def stop(self):
        """Bezpieczne zatrzymanie wątku z zewnątrz."""
        self.message_queue.put(None)