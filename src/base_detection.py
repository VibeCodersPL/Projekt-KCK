import cv2
import mediapipe as mp
import time
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class BaseDetection:
    def __init__(self):
        self.POSE_CONNECTIONS = [
            (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # Ramiona
            (11, 23), (12, 24), (23, 24),  # Tułów
            (16, 18), (16, 22), (16, 20), (18, 20),  # Prawa dłoń
            (15, 21), (15, 19), (15, 17), (17, 19),  # Lewa dłoń
            (24, 26), (26, 28), (28, 30), (28, 32), (30, 32),  # Prawa noga
            (23, 25), (25, 27), (27, 31), (27, 29), (31, 29)  # Lewa noga
        ]

        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'pose_landmarker_lite.task')

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO
        )

        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def process_frame(self, frame):

        h, w, _ = frame.shape

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp = int(time.time() * 1000)

        result = self.landmarker.detect_for_video(mp_image, timestamp)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

            for connection in self.POSE_CONNECTIONS:
                start_point = landmarks[connection[0]]
                end_point = landmarks[connection[1]]
                cv2.line(frame,
                         (int(start_point.x * w), int(start_point.y * h)),
                         (int(end_point.x * w), int(end_point.y * h)),
                         (255, 255, 0), 2)

            for lm in landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        return frame, result

    def close(self):
        self.landmarker.close()
