import math
import cv2
import mediapipe as mp
import time
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # Ramiona
    (11, 23), (12, 24), (23, 24)  # Tułów
]




# Konfiguracja Tasks
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'pose_landmarker_lite.task')

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO
)

cap = cv2.VideoCapture(0)

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        h, w, _ = frame.shape
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        timestamp = int(time.time() * 1000)

        result = landmarker.detect_for_video(mp_image, timestamp)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

            for connection in POSE_CONNECTIONS:
                start_point = landmarks[connection[0]]
                end_point = landmarks[connection[1]]
                cv2.line(frame,
                         (int(start_point.x * w), int(start_point.y * h)),
                         (int(end_point.x * w), int(end_point.y * h)),
                         (255, 255, 0), 2)

            for lm in landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        cv2.imshow('MediaPipe Tasks - No Solutions', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()