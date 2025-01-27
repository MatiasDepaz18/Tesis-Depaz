import cv2
import mediapipe as mp
import time

# Inicializa MediaPipe FaceLandmarker
mp_face_mesh = mp.solutions.face_mesh

# Configura el FaceMesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

#Cargo para dibujar bien los contornos
mp_drawing = mp.solutions.drawing_utils 
mp_drawing_styles = mp.solutions.drawing_styles

# Inicializa la cámara
cap = cv2.VideoCapture(0)  

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

while True:
    start_time=time.time() #Empieza a contar el tiempo que toma la captura

    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer un cuadro de video.")
        break

    # Convierte el cuadro a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Procesa el cuadro para detectar puntos faciales
    results = face_mesh.process(frame_rgb)

    # Dibuja los puntos faciales en el cuadro
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            #Esto me hace la malla sin los puntos
            mp_drawing.draw_landmarks(
                frame,face_landmarks,mp_face_mesh.FACEMESH_TESSELATION,None,mp_drawing_styles.get_default_face_mesh_tesselation_style())
            
            #Esto me marca los bordes solamente
            mp_drawing.draw_landmarks(
                frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS,None,mp_drawing_styles.get_default_face_mesh_contours_style())

#            #Esto me hace la malla en los iris (Tal vez no me sirva tanto en un futuro)
#            mp_drawing.draw_landmarks(
#                frame,face_landmarks,mp_face_mesh.FACEMESH_IRISES,None,mp_drawing_styles.get_default_face_mesh_iris_connections_style())


    # Mide el tiempo de procesamiento
    end_time = time.time()  # Marca de tiempo final
    processing_time = (end_time - start_time) * 1000  # Convertir a milisegundos
    print(f"Tiempo de procesamiento por frame: {processing_time:.2f} ms")
    
    # Muestra el video
    cv2.imshow("Face Landmarks", frame)

    # Salir al presionar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera la cámara y cierra las ventanas
cap.release()
cv2.destroyAllWindows()
