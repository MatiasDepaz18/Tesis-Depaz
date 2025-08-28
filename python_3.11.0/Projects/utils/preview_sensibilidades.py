# utils/preview_sensibilidad.py

import cv2
import mediapipe as mp
import numpy as np
from utils.constants import *
from logic.metrics import *

def mostrar_preview():
    cap = cv2.VideoCapture(1)

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    )
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                lm = face_landmarks.landmark

                left_ear = calculate_ear(lm, LEFT_EYE)
                right_ear = calculate_ear(lm, RIGHT_EYE)
                mouth = calculate_mouth_openness(lm,MOUTH)
                # ceja_derecha = calculate_eyebrow_lift(lm)

                cv2.putText(frame, f"Ojo derecho: {left_ear:.3f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 0) if left_ear > 0.2 else (0, 0, 255), 2)
                cv2.putText(frame, f"Ojo izquierdo: {right_ear:.3f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 0) if right_ear > 0.2 else (0, 0, 255), 2)
                cv2.putText(frame, f"Boca: {mouth:.3f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 0) if mouth > 0.06 else (0, 0, 255), 2)
                # cv2.putText(frame, f"Ceja derecha: {ceja_derecha:.3f}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                #             (0, 255, 0), 2)

                mp_drawing.draw_landmarks(
                    frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS, None,
                    mp_drawing_styles.get_default_face_mesh_contours_style()
                )
                mp_drawing.draw_landmarks(
                    frame, face_landmarks, mp_face_mesh.FACEMESH_IRISES, None,
                    mp_drawing_styles.get_default_face_mesh_iris_connections_style()
                )

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == -1 and cv2.getWindowProperty("Frame", cv2.WND_PROP_VISIBLE) <= 0:
            break
        elif key & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
