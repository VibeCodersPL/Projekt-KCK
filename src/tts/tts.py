import os
import tempfile
import threading
import queue
from gtts import gTTS
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

class TTS:
    def __init__(self):
        self.message_queue = queue.Queue()
        self.is_speaking = False
        self._current_sound = None
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = os.path.join(base_dir, '..', '..', 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.thread = threading.Thread(target=self._speak_task, daemon=True)
        self.thread.start()

    def _speak_task(self):
        print("[TTS] Wątek gTTS startuje.", flush=True)

        while True:
            phrase = self.message_queue.get()
            if phrase is None:
                print("[TTS] Zamykanie wątku TTS.", flush=True)
                break

            self.is_speaking = True
            print(f"[TTS] Pobieram audio dla: {phrase}", flush=True)
            temp_path = None
            
            try:
                tts = gTTS(text=phrase, lang='pl')
                fd, temp_path = tempfile.mkstemp(suffix=".mp3", dir=self.temp_dir)
                os.close(fd)
                tts.save(temp_path)
                
                print(f"[TTS] Odtwarzanie pliku: {temp_path}", flush=True)
                self._play_audio_sync(temp_path)
                
            except Exception as e:
                print(f"[TTS] Błąd gTTS: {e}", flush=True)
            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception as e:
                        print(f"[TTS] Ostrzeżenie - nie można usunąć pliku: {e}", flush=True)
                
                self.is_speaking = False
                self.message_queue.task_done()
                print("[TTS] Zakończono frazę.", flush=True)

    def _play_audio_sync(self, path):
        """Synchronizuje odtwarzanie dźwięku z głównym wątkiem interfejsu Kivy."""
        playback_event = threading.Event()
        Clock.schedule_once(lambda dt: self._kivy_play(path, playback_event), 0)
        playback_event.wait(timeout=10.0)

    def _kivy_play(self, path, playback_event):
        """Ta metoda JEST wykonywana w głównym wątku Kivy."""
        self._current_sound = SoundLoader.load(path)
        
        if self._current_sound:
            self._current_sound.play()
            
            duration = self._current_sound.length if self._current_sound.length > 0 else 3.0
            
            def on_finish(dt):
                if self._current_sound:
                    self._current_sound.stop()
                    self._current_sound.unload()
                    self._current_sound = None
                playback_event.set()
            
            Clock.schedule_once(on_finish, duration + 0.2)
        else:
            print("[TTS] SoundLoader Kivy nie mógł załadować pliku MP3.", flush=True)
            playback_event.set()

    def speak(self, phrase):
        """Dodaje frazę do kolejki. Zabezpiecza przed spamem."""
        if not self.is_speaking and self.message_queue.empty():
            print(f"[TTS] Dodano do kolejki: {phrase}", flush=True)
            self.message_queue.put(phrase)

    def stop(self):
        with self.message_queue.mutex:
            self.message_queue.queue.clear()
        Clock.schedule_once(self._force_stop, 0)

    def _force_stop(self, dt):
        if getattr(self, '_current_sound', None):
            self._current_sound.stop()
            self._current_sound.unload()
            self._current_sound = None

        self.is_speaking = False
