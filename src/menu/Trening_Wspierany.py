import detection.excersises as ex
from kivy.core.image import Texture
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import cv2
from TwoCameraFrameWindow import TwoCameraFrameWindow as TCFW
from RoundedButton import *

class TreningWspierany(TCFW):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screenExcersise = ex.LowReady()

        self.is_training_started = False # Czy trening już się zaczął
        self.hover_start_frames = 0 # licznik "czasu" jaki musi minąć aby uruchomić przycisk start/stop
        self.hover_save_frames = 0 # licznik "czasu" dla przycisku zapisz
        self.HOVER_THRESHOLD = 30 # ile czasu potrzba aby aktywować przyciski
        self.has_training_run = False  # Czy było start i potem stop (trening się zaczął i skończyć -> można go zapisać)
        self.is_training_saved = False  # Czy trening został już zapisany
        self.is_pose_correct = False

    def update_frame(self, dt):
        if not self.cap or not self.cap.isOpened() and not self.cap2 or not self.cap2.isOpened():
            return

        landmarksFront = None
        landmarksSide = None

        if self.cap.isOpened():
            self.camera_view.texture, landmarksFront = self.update_camera(self.cap)

        if self.cap2.isOpened():
            self.camera_view2.texture, landmarksSide = self.update_camera(self.cap2, True)

        if self.is_training_started:
            self.is_pose_correct = self.screenExcersise.checkExcersise(landmarksFront, landmarksSide)

            msg = self.screenExcersise.getMessage()
            #self.text_box.text = msg
        else:
            self.is_pose_correct = False
           # self.text_box.text = "Czekam na start..."

    def update_camera(self, cap, isSide: bool = False):
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)

            processed_frame, result = self.detector.process_frame(frame)
            landmarks = self.detector.getLandmarks()

            if not isSide:
                processed_frame = self.handle_cv_interface(processed_frame)

            buf = cv2.flip(processed_frame, 0).tobytes()
            texture = Texture.create(
                size=(processed_frame.shape[1], processed_frame.shape[0]),
                colorfmt='bgr'
            )
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            return texture, landmarks

        return None, None

    def handle_cv_interface(self, frame):
        h, w, _ = frame.shape

        btn_w, btn_h = int(w * 0.20), int(h * 0.12)

        # Przycisk start/stop
        s_x1, s_y1 = int(w * 0.05), int(h * 0.15)
        s_x2, s_y2 = s_x1 + btn_w, s_y1 + btn_h

        # Przycisk zapisz
        sv_x1 = w - btn_w - int(w * 0.05)
        sv_y1 = s_y1
        sv_x2, sv_y2 = sv_x1 + btn_w, sv_y1 + btn_h

        #sprawdzenie reakcji przycisku zapisz
        can_save = self.has_training_run and not self.is_training_started and not self.is_training_saved

        wrists = []
        for idx in [15, 16]:
            lm = self.detector.getLandmarkCords(idx)
            if lm:
                wrists.append((int(lm[0] * w), int(lm[1] * h)))

        start_hovered = False
        save_hovered = False

        for wx, wy in wrists:
            # Kolizja ze Start/Stop
            if s_x1 <= wx <= s_x2 and s_y1 <= wy <= s_y2:
                start_hovered = True
            # Kolizja z Zapisz (aktywna tylko, gdy spełnione są warunki zapisu)
            if sv_x1 <= wx <= sv_x2 and sv_y1 <= wy <= sv_y2:
                if can_save:
                    save_hovered = True

        # Logika hover dla Start/Stop
        if start_hovered:
            if self.hover_start_frames >= 0:
                self.hover_start_frames += 1
                if self.hover_start_frames >= self.HOVER_THRESHOLD:
                    self.toggle_start_stop()
                    self.hover_start_frames = -30
        else:
            self.hover_start_frames = max(0, self.hover_start_frames - 2) \
                if self.hover_start_frames > 0 else self.hover_start_frames

        if self.hover_start_frames < 0:
            self.hover_start_frames += 1

        # Logika hover dla Zapisz
        if save_hovered:
            if self.hover_save_frames >= 0:
                self.hover_save_frames += 1
                if self.hover_save_frames >= self.HOVER_THRESHOLD:
                    self.save_training()
                    self.hover_save_frames = -30
        else:
            self.hover_save_frames = max(0,
                                         self.hover_save_frames - 2) if self.hover_save_frames > 0 else self.hover_save_frames

        if self.hover_save_frames < 0:
            self.hover_save_frames += 1

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = w / 1200.0
        thickness = 1

        if self.is_training_started:
            if self.is_pose_correct:
                status_text = "DOBRZE!"
                status_color = (0, 255, 0)  # Zielony (BGR)
            else:
                status_text = "SKORYGUJ POSTAWE"
                status_color = (0, 0, 255)  # Czerwony (BGR)

            big_font_scale = font_scale * 1.5
            big_thickness = thickness + 1

            (st_w, st_h), _ = cv2.getTextSize(status_text, font, big_font_scale, big_thickness)
            st_x = (w - st_w) // 2
            st_y = int(h * 0.1)

            cv2.putText(frame, status_text, (st_x, st_y), font, big_font_scale, (0, 0, 0),
                        big_thickness + 2)
            cv2.putText(frame, status_text, (st_x, st_y), font, big_font_scale, status_color,
                        big_thickness)

        # przycisk start-stop
        bg_start = (0, 0, 200) if self.is_training_started else (0, 180, 0)
        cv2.rectangle(frame, (s_x1, s_y1), (s_x2, s_y2), bg_start, -1)

        if self.hover_start_frames > 0:
            fill_w = int((self.hover_start_frames / self.HOVER_THRESHOLD) * btn_w)
            cv2.rectangle(frame, (s_x1, s_y1), (s_x1 + fill_w, s_y2), (0, 255, 255), -1)

        text_start = "STOP" if self.is_training_started else "START"

        (t_w, t_h), _ = cv2.getTextSize(text_start, font, font_scale, thickness)
        t_x = s_x1 + (btn_w - t_w) // 2
        t_y = s_y1 + (btn_h + t_h) // 2
        cv2.putText(frame, text_start, (t_x, t_y), font, font_scale, (255, 255, 255), thickness)

        # Przycisk zapisz
        if self.is_training_saved:
            bg_save = (150, 0, 0)  # ciemno niebieski - potwierdzenie zapisu
            text_save = "ZAPISANO"
        elif can_save:
            bg_save = (200, 100, 0)  # Niebieski -
            text_save = "ZAPISZ"
        else:
            bg_save = (100, 100, 100)  # Szary - zablokowany
            text_save = "ZAPISZ"

        cv2.rectangle(frame, (sv_x1, sv_y1), (sv_x2, sv_y2), bg_save, -1)

        if self.hover_save_frames > 0 and can_save:
            fill_w = int((self.hover_save_frames / self.HOVER_THRESHOLD) * btn_w)
            cv2.rectangle(frame, (sv_x1, sv_y1), (sv_x1 + fill_w, sv_y2), (0, 255, 255), -1)

        (t_w, t_h), _ = cv2.getTextSize(text_save, font, font_scale, thickness)
        t_x = sv_x1 + (btn_w - t_w) // 2
        t_y = sv_y1 + (btn_h + t_h) // 2
        cv2.putText(frame, text_save, (t_x, t_y), font, font_scale, (255, 255, 255), thickness)

        return frame

    def toggle_start_stop(self):
        self.is_training_started = not self.is_training_started

        if self.is_training_started:
            print("Trening ROZPOCZĘTY")
            self.has_training_run = False
            self.is_training_saved = False
        else:
            print("Trening ZATRZYMANY")
            self.has_training_run = True

        # TODO logika do startu stopu przycisku

    def save_training(self):
        print("Trening ZAPISANY!")
        self.is_training_saved = True  
        # TODO logika zapisu treningu

    def change_screen(self, target_screen, instance):
        if target_screen == 'menu':
            self.show_exit_confirmation(target_screen)
        else:
            super().change_screen(target_screen, instance)

    def show_exit_confirmation(self, target_screen):
        content_layout = BoxLayout(orientation='vertical', spacing=20, padding=20)

        msg_label = Label(
            text="Czy chcesz przerwać trening i wyjść?",
            size_hint_y=0.7,
            halign='center',
            valign='middle',
            font_size = '24sp'
        )
        msg_label.bind(size=msg_label.setter('text_size'))

        buttons_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.3)

        btn_yes = RoundedButton(text="Tak",
                    font_size='26sp',
                    color=(1, 1, 1, 1),
                    bg_color=(0.15, 0.45, 0.85, 1),
                    radius=45)
        btn_no = RoundedButton(text="Nie",
                    font_size='26sp',
                    color=(1, 1, 1, 1),
                    bg_color=(0.15, 0.45, 0.85, 1),
                    radius=45)

        buttons_layout.add_widget(btn_yes)
        buttons_layout.add_widget(btn_no)

        content_layout.add_widget(msg_label)
        content_layout.add_widget(buttons_layout)

        self.exit_popup = Popup(
            title='Przerwanie treningu',
            content=content_layout,
            size_hint=(0.4, 0.4),
            auto_dismiss=False
        )

        btn_yes.bind(on_press=lambda inst: self.confirm_exit(target_screen))
        btn_no.bind(on_press=self.exit_popup.dismiss)

        self.exit_popup.open()

    def confirm_exit(self, target_screen):
        self.exit_popup.dismiss()
        print("Trening przerwany. Ćwiczenie nie zostało zapisane.")
        self.manager.current = target_screen