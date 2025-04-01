import cv2
import mediapipe as mp
import numpy as np
import time
from pynput.keyboard import Controller 

# Inicializa MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True ,min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Inicializa la cámara
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

# Variables de estado
left_eye_pressed = False  # Indica si 'A' está presionada
right_eye_pressed = False  # Indica si 'D' está presionada
mouse_pressed = False      #Indica si 'W' esta presionada

# Función para calcular EAR
def calculate_ear(landmarks, eye_points):
    """Calcula el Eye Aspect Ratio (EAR)"""
    p1, p2, p3, p4, p5, p6 = [np.array([landmarks[p].x, landmarks[p].y]) for p in eye_points]
    vertical_1 = np.linalg.norm(p2 - p6)
    vertical_2 = np.linalg.norm(p3 - p5)
    horizontal = np.linalg.norm(p1 - p4)
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear
def calcular_mouse(landmarks, mouse_points):
    "Calculare la distancia con la boca cerrada"
    p1, p2= [np.array([landmarks[p].y]) for p in mouse_points]
    mouse_distance=np.linalg.norm(p1 - p2)
    return mouse_distance

# Índices de los puntos del ojo izquierdo y derecho
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
MOUSE=[0,17]

#Variables inicializadas para el inicio
mouse_was_closed=False
left_eye_was_closed = False
right_eye_was_closed = False

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

            # Calcula la distancia de la boca
            mouse_status= calcular_mouse(landmarks,MOUSE)

            # Esto me sirve para modificar el rango de ojo abierto o cerrado
            EAR_THRESHOLD = 0.22
            MOUSE_THRESHOLD = 0.10

            # Determina si los ojos están cerrados
            left_eye_closed = left_ear < EAR_THRESHOLD
            right_eye_closed = right_ear < EAR_THRESHOLD
            mouse_closed = mouse_status < MOUSE_THRESHOLD

            keyboard = Controller()

            # Detecta transición de abierto a cerrado para cada ojo
            if left_eye_closed and not left_eye_pressed:
                print("🔵 Ojo izquierdo cerrado: presionando tecla 'D'")
                keyboard.press('d')
                left_eye_pressed = True  # Marca que la tecla está presionada
            
            elif not left_eye_closed and left_eye_pressed:
                print("🔵 Ojo izquierdo abierto: soltando tecla 'D'")
                keyboard.release('d')
                left_eye_pressed = False  # Marca que la tecla fue liberada

            # Ojo derecho → 'D'
            if right_eye_closed and not right_eye_pressed:
                print("🟢 Ojo derecho cerrado: presionando tecla 'A'")
                keyboard.press('a')
                right_eye_pressed = True  
            
            elif not right_eye_closed and right_eye_pressed:
                print("🟢 Ojo derecho abierto: soltando tecla 'A'")
                keyboard.release('a')
                right_eye_pressed = False  
            
            if mouse_closed and not mouse_pressed:
                print("🟢 Boca cerrada: presionando tecla 'w'")
                keyboard.release('w')
                mouse_pressed = True  # Marca que la tecla esta presionada

            elif not mouse_closed and mouse_pressed:
                keyboard.press('w')
                mouse_pressed = False  # Marca que la tecla fue liberada
                          
            # Actualiza los estados
            left_eye_was_closed = left_eye_closed
            right_eye_was_closed = right_eye_closed
            mouse_was_closed = mouse_closed

            # Dibuja el estado del ojo izquierdo
            cv2.putText(frame, f"Ojo izquierdo: {'Cerrado' if left_eye_closed else 'Abierto'}", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                        (0, 255, 0) if not left_eye_closed else (0, 0, 255), 2)

            # Dibuja el estado del ojo derecho
            cv2.putText(frame, f"Ojo derecho: {'Cerrado' if right_eye_closed else 'Abierto'}", 
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                        (0, 255, 0) if not right_eye_closed else (0, 0, 255), 2)
            
            #Pongo la distancia de la boca
            cv2.putText(frame, f"Boca: {'Cerrado' if mouse_closed else 'Abierto'}", 
                        (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                        (0, 255, 0) if not left_eye_closed else (0, 0, 255), 2)
            
            # Dibuja los landmarks faciales
            mp_drawing.draw_landmarks(
                frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS, None,
                mp_drawing_styles.get_default_face_mesh_contours_style()
            )
            #Esto me hace la malla en los iris (Tal vez no me sirva tanto en un futuro)
            mp_drawing.draw_landmarks(
                frame,face_landmarks,mp_face_mesh.FACEMESH_IRISES,None,
                mp_drawing_styles.get_default_face_mesh_iris_connections_style())            

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

