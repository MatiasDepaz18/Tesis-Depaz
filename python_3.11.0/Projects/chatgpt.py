import cv2
import mediapipe as mp
import numpy as np
import time

# Inicializa MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Inicializa la cámara
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

# Función para calcular EAR
def calculate_ear(landmarks, eye_points):
    """Calcula el Eye Aspect Ratio (EAR)"""
    p1, p2, p3, p4, p5, p6 = [np.array([landmarks[p].x, landmarks[p].y]) for p in eye_points]
    vertical_1 = np.linalg.norm(p2 - p6)
    vertical_2 = np.linalg.norm(p3 - p5)
    horizontal = np.linalg.norm(p1 - p4)
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear

# Índices de los puntos del ojo izquierdo y derecho
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

while True:
    start_time = time.time()  # Marca de tiempo inicial
    
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer un cuadro de video.")
        break

    # Convierte el cuadro a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Procesa el cuadro para detectar puntos faciales
    results = face_mesh.process(frame_rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark

            # Calcula EAR para ambos ojos
            left_ear = calculate_ear(landmarks, LEFT_EYE)
            right_ear = calculate_ear(landmarks, RIGHT_EYE)

            # Determina si los ojos están cerrados
            EAR_THRESHOLD = 0.25
            left_eye_status = "Cerrado" if left_ear < EAR_THRESHOLD else "Abierto"
            right_eye_status = "Cerrado" if right_ear < EAR_THRESHOLD else "Abierto"

            # Dibuja el estado del ojo en el cuadro
            cv2.putText(frame, f"Ojo izquierdo: {left_eye_status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Ojo derecho: {right_eye_status}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Dibuja los landmarks faciales
            mp_drawing.draw_landmarks(
                frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS, None,
                mp_drawing_styles.get_default_face_mesh_contours_style()
            )

    end_time = time.time()
    processing_time = (end_time - start_time) * 1000
    print(f"Tiempo de procesamiento por frame: {processing_time:.2f} ms")

    # Muestra el video
    cv2.imshow("Face Landmarks", frame)

    # Salir al presionar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

