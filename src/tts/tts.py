import threading
import queue
import os
import time
from gtts import gTTS
from kivy.clock import mainthread
from kivy.core.audio import SoundLoader


class TTS:
    def __init__(self):
        self.message_queue = queue.Queue()
        self.sound = None
        self.counter = 0
        self.save_dir = os.path.dirname(os.path.abspath(__file__))

        self.thread = threading.Thread(target=self._speak_task, daemon=True)
        self.thread.start()

    def _speak_task(self):
        while True:
            phrase = self.message_queue.get()
            if phrase is None:
                break

            try:
                tts = gTTS(text=phrase, lang='pl', slow=False)
                filename = os.path.join(self.save_dir, f"kivy_trener_tts_{self.counter}.mp3")
                tts.save(filename)

                self._play_in_kivy(filename)
                time.sleep(0.2)
                while self.sound and self.sound.state == 'play':
                    time.sleep(0.1)

                self.counter = (self.counter + 1) % 10

            except Exception as e:
                print(f"Błąd Google TTS: {e}")
            finally:
                self.message_queue.task_done()

    @mainthread
    def _play_in_kivy(self, filepath):
        if self.sound:
            self.sound.stop()
            self.sound.unload()

        self.sound = SoundLoader.load(filepath)
        if self.sound:
            self.sound.play()

    @mainthread
    def _stop_kivy_sound(self):
        if self.sound:
            self.sound.stop()

    def interrupt(self):
        with self.message_queue.mutex:
            self.message_queue.queue.clear()
        self._stop_kivy_sound()

    def speak(self, phrase):
        self.message_queue.put(phrase)

    def stop(self):
        self.message_queue.put(None)