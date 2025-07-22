import numpy as np

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