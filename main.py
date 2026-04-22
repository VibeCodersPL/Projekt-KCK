import math
import cv2
import mediapipe as mp
import time
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Definicja połączeń między punktami (zgodnie ze schematem Pose Landmarker)
# Wybrany zestaw połączeń dla ramion i tułowia
POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # Ramiona
    (11, 23), (12, 24), (23, 24)  # Tułów
]


def Calculate3PointsDegree(left, mid, right):
    def dis(p1, p2):
        return math.sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2))

    try:
        res = (math.pow(dis(mid, left), 2) + math.pow(dis(mid, right), 2) - math.pow(dis(right, left), 2)) / (
                2 * dis(left, mid) * dis(right, mid))
        return math.degrees(math.acos(max(-1.0, min(1.0, res))))
    except:
        return 0


class BodyLandmarks:
    def __init__(self):
        self.landmarks = None

    def set(self, landmarks):
        self.landmarks = landmarks

    def get_angle(self, p1_idx, p2_idx, p3_idx):
        return Calculate3PointsDegree(self.landmarks[p1_idx], self.landmarks[p2_idx], self.landmarks[p3_idx])

    def detect(self):
        if not self.landmarks: return "Brak"

        # Pobieranie kątów (indeksy: bark=11/12, łokieć=13/14, nadgarstek=15/16, biodro=23/24)
        l_shoulder_angle = self.get_angle(23, 11, 15)
        r_shoulder_angle = self.get_angle(24, 12, 16)
        l_elbow_angle = self.get_angle(11, 13, 15)
        r_elbow_angle = self.get_angle(12, 14, 16)

        # T: Ręce prostopadle do tułowia
        if abs(90 - l_shoulder_angle) < 25 and abs(90 - r_shoulder_angle) < 25:
            return "T"
        # Y: Ręce uniesione pod kątem
        if 130 < l_shoulder_angle < 170 and 130 < r_shoulder_angle < 170:
            return "Y"
        # I: Ręce pionowo w górę
        if l_shoulder_angle > 170 and r_shoulder_angle > 170:
            return "I"
        # L: Prawa ręka w górę, lewa w bok
        if r_shoulder_angle > 160 and abs(90 - l_shoulder_angle) < 25:
            return "L"

        return "Brak"


# Konfiguracja Tasks
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'pose_landmarker_lite.task')

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO
)

bdlm = BodyLandmarks()
cap = cv2.VideoCapture(0)

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        h, w, _ = frame.shape
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        timestamp = int(time.time() * 1000)

        result = landmarker.detect_for_video(mp_image, timestamp)
        litera = "Brak"

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]
            bdlm.set(landmarks)
            litera = bdlm.detect()
            # RYSOWANIE RĘCZNE (bez solutions) test
            # RYSOWANIE RĘCZNE (bez solutions) test
            # RYSOWANIE RĘCZNE (bez solutions) test
            # RYSOWANIE RĘCZNE (bez solutions)
            # 1. Rysowanie linii (połączeń)
            for connection in POSE_CONNECTIONS:
                start_point = landmarks[connection[0]]
                end_point = landmarks[connection[1]]
                cv2.line(frame,
                         (int(start_point.x * w), int(start_point.y * h)),
                         (int(end_point.x * w), int(end_point.y * h)),
                         (255, 255, 0), 2)

            # 2. Rysowanie punktów
            for lm in landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        cv2.putText(frame, f'LITERA: {litera}', (30, 70),
                    cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 3)

        cv2.imshow('MediaPipe Tasks - No Solutions', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()