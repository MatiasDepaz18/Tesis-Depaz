# utils/preview_sensibilidad.py

import cv2
import mediapipe as mp
import numpy as np
from utils.constants import *
from logic.metrics import *
from utils.camara_selector import seleccionar_camara_con_nombre

def draw_text_with_bg(frame, text, pos, color, bg_color=(0,0,0), alpha=0.5):
    (x, y) = pos
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    (w, h), _ = cv2.getTextSize(text, font, font_scale, thickness)
    # Crear overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (x-5, y-h-5), (x+w+5, y+10), bg_color, -1)
    # Mezclar overlay con el frame original
    cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0, frame)
    # Escribir el texto encima
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)

def mostrar_preview(valores = None):
    print(valores)
    cam_index = seleccionar_camara_con_nombre()
    cap = cv2.VideoCapture(cam_index)
    ear_thr_left = 0.22
    ear_thr_right = 0.22
    mouth_thr = 0.06
    eyebrow_thr = 0.06
    roll_thr_left = 12.0
    roll_thr_right = 12.0
    pitch_up_thr = 20.0
    pitch_down_thr = 40.0

    if valores:
        ear_thr_left = float(valores.get("left_eye", 0)) * 0.01
        ear_thr_right = float(valores.get("right_eye", 0)) * 0.01
        mouth_thr = float(valores.get("mouth", 0)) * 0.001
        eyebrow_thr = float(valores.get("eyebrows", 0)) * 0.001
        roll_thr_left = float(valores.get("roll_left", 12.0))
        roll_thr_right = float(valores.get("roll_right", 12.0))
        pitch_up_thr = float(valores.get("pitch_up", 20.0))
        pitch_down_thr = float(valores.get("pitch_down", 40.0))

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

                left_ear = calculate_ear(lm, RIGHT_EYE)
                right_ear = calculate_ear(lm, LEFT_EYE)
                mouth = calculate_mouth_openness(lm, MOUTH)
                left_lift = calculate_eyebrow_lift(lm, EYEBROW_LEFT, EYE_CENTER_LEFT)
                right_lift = calculate_eyebrow_lift(lm, EYEBROW_RIGHT, EYE_CENTER_RIGHT)
                avg_lift   = (left_lift + right_lift) / 2.0
                # Umbral (podés tocarlo o tomarlo del config si querés)
                eyebrow_thr = EYEBROW_THRESHOLD
                roll = calculate_roll_deg(lm, LEFT_EYE, RIGHT_EYE, frame.shape) 
                pitch = calculate_pitch_deg(lm, LEFT_EYE, RIGHT_EYE, frame.shape)

                draw_text_with_bg(frame, f"Ojo Izquierdo: {left_ear*100:.2f}", (10, 30), (0,255,0) if left_ear > ear_thr_left else (0,0,255))
                draw_text_with_bg(frame, f"Ojo Derecho: {right_ear*100:.2f}", (10, 60), (0,255,0) if right_ear > ear_thr_right else (0,0,255))
                draw_text_with_bg(frame, f"Boca: {mouth*1000:.2f}", (10, 90), (0,255,0) if mouth > mouth_thr else (0,0,255))
                draw_text_with_bg(frame, f"Cejas (promedio): {avg_lift*1000:.2f}", (10, 120), (0,255,0) if avg_lift > eyebrow_thr else (0,0,255))
                draw_text_with_bg(frame, f"Roll: {roll:+.1f} deg", (10, 150), (0,255,0) if abs(roll) > min(roll_thr_left, roll_thr_right) else (0,0,255))
                draw_text_with_bg(frame, f"Pitch: {pitch:+.1f} deg", (10, 180), (0,255,0))
                # Pitch Up: ACTIVO si pitch < pitch_up_thr
                draw_text_with_bg(frame, f"Pitch Up: {'ACTIVO' if pitch < pitch_up_thr else '---'}", (10, 210), (0,255,0) if pitch < pitch_up_thr else (0,0,255))
                # Pitch Down: ACTIVO si pitch > pitch_down_thr
                draw_text_with_bg(frame, f"Pitch Down: {'ACTIVO' if pitch > pitch_down_thr else '---'}", (10, 240), (0,255,0) if pitch > pitch_down_thr else (0,0,255))

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

if __name__ == "__main__":
    mostrar_preview()
