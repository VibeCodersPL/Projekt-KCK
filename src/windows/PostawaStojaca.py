import json
from windows.Wzorowy_Pokaz import *
from tts.tts import *
from pathlib import Path

class PostawaStojaca(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speak_event = None
        JSON_PATH = Path(__file__).resolve().parents[1] / "tts" / "phrases.json"
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            self.phrases = json.load(f)
        root = AnchorLayout(anchor_x='center', anchor_y='center')
        layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(1000, 700), spacing=20)
        self.image_widget = Image(
            source="./assets/postawa_stojaca.png",
            size_hint=(1, 0.8),
            allow_stretch=True,
            keep_ratio=True
        )
        layout.add_widget(self.image_widget)
        self.menu_buttons = []
        btn_powrot = RoundedButton(
            text='Powrót',
            font_size='36sp',
            color=(1, 1, 1, 1),
            bg_color=(0.85, 0.15, 0.15, 1),
            radius=30,
            size_hint=(0.4, 0.2),
            pos_hint={'center_x': 0.5}
        )
        btn_powrot.bind(on_press=partial(self.change_screen, 'WzorowyPokaz'))
        layout.add_widget(btn_powrot)
        self.menu_buttons.append(btn_powrot)
        root.add_widget(layout)
        self.add_widget(root)
        self.cursor = Image(
            source='./assets/lapka1.png',
            size_hint=(None, None),
            size=(100, 100),
            pos=(-100, -100)
        )
        self.add_widget(self.cursor)
        self.detector = None
        self.cap = None
        self.update = None
        self.button_hover = None
        self.button_hover_start = None
        self.fill_color = None
        self.fill_rectangle = None

    def clean(self):
        if self.button_hover and self.fill_color and self.fill_rectangle:
            if self.fill_color in self.button_hover.canvas.after.children:
                self.button_hover.canvas.after.remove(self.fill_color)
            if self.fill_rectangle in self.button_hover.canvas.after.children:
                self.button_hover.canvas.after.remove(self.fill_rectangle)
        self.fill_color = None
        self.fill_rectangle = None

    def on_enter(self, *args):
        self.detector = self.manager.shared_detector_front
        self.tts = self.manager.shared_tts
        Clock.schedule_once(self._late_camera_init, 0.2)
        self.speak_event = Clock.schedule_once(self.speak_phrases, 2)

    def speak_phrases(self, dt):
        caly_tekst = self.phrases.get("WzorowyPokazStojaca", [])
        pelne_zdanie = " ".join([tekst.strip() for tekst in caly_tekst if tekst.strip()])
        if pelne_zdanie:
            self.tts.speak(pelne_zdanie)

    def _late_camera_init(self, dt):
        self.cap = cv2.VideoCapture(1)
        if self.cap.isOpened():
            self.update = Clock.schedule_interval(self.update_frame, 1 / 30)
        else:
            print("Kamera nadal zablokowana przez system.")

    def on_leave(self, *args):
        if self.speak_event:
            self.speak_event.cancel()
        if self.tts:
            self.tts.stop()
        if self.update:
            self.update.cancel()
            self.update = None
        if self.cap:
            self.cap.release()
            self.cap = None
        self.detector = None
        self.clean()
        self.button_hover = None
        self.cursor.pos = (-100, -100)
        self.cursor.source = "./assets/lapka1.png"

    def update_frame(self, dt):
        if not self.cap or not self.cap.isOpened():
            return

        temp, frame = self.cap.read()
        if not temp:
            return
        frame = cv2.flip(frame, 1)
        _, result = self.detector.process_frame(frame)
        cursor_pos = None
        cursor_pos = self.detector.getLandmarkCords(19);

        if cursor_pos is not None:
            x, y = cursor_pos
            win_x = x * Window.width
            win_y = (1 - y) * Window.height
            self.cursor.pos = (win_x - self.cursor.width / 2, win_y - self.cursor.height / 2)
            collision = None
            for button in self.menu_buttons:
                if button.collide_point(win_x, win_y):
                    collision = button
                    break

            if collision:
                if self.button_hover != collision:
                    self.clean()
                    self.button_hover = collision
                    self.button_hover_start = time.time()
                    self.cursor.source = "./assets/lapka2.png"
                    with self.button_hover.canvas.after:
                        self.fill_color = Color(0.1, 0.8, 0.2, 0.5)
                        self.fill_rectangle = RoundedRectangle(
                            pos=self.button_hover.pos,
                            size=(self.button_hover.width, 0),
                            radius=[30, 30, 30, 30],
                        )
                else:
                    elapsed_time = time.time() - self.button_hover_start
                    progress = min(1.0, elapsed_time / 2.0)
                    if self.fill_rectangle:
                        new_height = self.button_hover.height * progress
                        self.fill_rectangle.size = (self.button_hover.width, new_height)

                        if elapsed_time > 2.0:
                            self.clean()
                            self.change_screen("WzorowyPokaz")
                            self.button_hover = None
                            self.cursor.source = "./assets/lapka1.png"
            else:
                if self.button_hover is not None:
                    self.clean()
                    self.button_hover = None
                    self.cursor.source = "./assets/lapka1.png"
        else:
            self.cursor.pos = (-100, -100)
            if self.button_hover is not None:
                self.clean()
                self.button_hover = None
                self.cursor.source = "./assets/lapka1.png"

    def change_screen(self, target_screen, *args):
        self.manager.current = target_screen
