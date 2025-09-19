import numpy as np
import math

def calculate_ear(landmarks, eye_points):
    p = [np.array([landmarks[i].x, landmarks[i].y]) for i in eye_points]
    vertical_1 = np.linalg.norm(p[1] - p[5])
    vertical_2 = np.linalg.norm(p[2] - p[4])
    horizontal = np.linalg.norm(p[0] - p[3])
    return (vertical_1 + vertical_2) / (2.0 * horizontal)

def calculate_mouth_openness(landmarks, mouth_points):
    p1, p2 = [np.array([landmarks[i].y]) for i in mouth_points]
    return np.linalg.norm(p1 - p2)

def calculate_eyebrow_lift(landmarks, brow_points, eye_center_points):
    p1 = np.array([landmarks[i].y for i in brow_points])
    p2 = np.array([landmarks[i].y for i in eye_center_points])
    return np.linalg.norm(p1 - p2)

def _pt_xy(lm, idx, w, h):
    return np.array([lm[idx].x * w, lm[idx].y * h], dtype=np.float32)

def _eye_angle_deg(landmarks, eye_points, image_shape):
    """Ángulo de la línea comisura↔comisura del ojo en grados (0 = horizontal).
       eye_points[0] y eye_points[3] deben ser los extremos del ojo."""
    h, w = image_shape[:2]
    p0 = _pt_xy(landmarks, eye_points[0], w, h)
    p3 = _pt_xy(landmarks, eye_points[3], w, h)
    dy, dx = (p3[1] - p0[1]), (p3[0] - p0[0])
    return math.degrees(math.atan2(dy, dx))

def calculate_roll_deg(landmarks, left_eye_points, right_eye_points, image_shape):
    """Promedia el ángulo de ambos ojos para estimar roll en grados.
       roll > 0 => línea ‘sube’ hacia la derecha (inclinación tipo ↗).
       roll < 0 => línea ‘baja’ hacia la derecha (inclinación tipo ↘)."""
    aL = _eye_angle_deg(landmarks, left_eye_points,  image_shape)
    aR = _eye_angle_deg(landmarks, right_eye_points, image_shape)
    return float((aL + aR) / 2.0)

def calculate_pitch_deg(landmarks, left_eye_points, right_eye_points, image_shape):
    """
    Calcula el ángulo de pitch (arriba/abajo) de la cabeza en grados.
    Usa la posición vertical de los ojos y la nariz.
    """
    h, w = image_shape[:2]
    # Usamos el centro entre los ojos y la nariz
    left_eye = _pt_xy(landmarks, left_eye_points[0], w, h)
    right_eye = _pt_xy(landmarks, right_eye_points[0], w, h)
    nose = _pt_xy(landmarks, 1, w, h)  # landmark 1 = nariz

    # Centro entre los ojos
    eyes_center = (left_eye + right_eye) / 2.0

    # Diferencia vertical entre nariz y centro de ojos
    dy = nose[1] - eyes_center[1]
    # Distancia horizontal entre ojos (para normalizar)
    dx_eyes = abs(left_eye[0] - right_eye[0])
    if dx_eyes == 0:
        return 0.0

    pitch_rad = np.arctan2(dy, dx_eyes)
    pitch_deg = np.degrees(pitch_rad)
    return pitch_deg