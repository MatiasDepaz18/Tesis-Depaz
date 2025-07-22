from detector.face_detector import FaceDetector
from controller.gesture_controller import GestureController
from logic.metrics import calculate_ear, calculate_mouth_openness, calculate_eyebrow_lift
from utils.constants import *

import cv2

detector = FaceDetector()
controller = GestureController()

while True:
    frame, results = detector.get_frame_and_landmarks()
    if frame is None:
        break

    if results and results.multi_face_landmarks:
        for face in results.multi_face_landmarks:
            lm = face.landmark
            gestures = {
                'left_eye': calculate_ear(lm, LEFT_EYE) < EAR_THRESHOLD,
                'right_eye': calculate_ear(lm, RIGHT_EYE) < EAR_THRESHOLD,
                'mouth': calculate_mouth_openness(lm, MOUTH) < MOUTH_THRESHOLD,
            }
            controller.update(gestures)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

detector.release()