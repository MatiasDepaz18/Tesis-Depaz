import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


model_path = "face_landmarker.task"


import cv2
import mediapipe as mp

# Import required components
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Ruta del modelo pre-entrenado (cambia esta ruta al modelo que estés usando)
model_path = "face_landmarker.task"


def print_result(result, output_image, timestamp_ms):
    print(f'Face landmarks detected at timestamp {timestamp_ms}ms')

# Función para manejar los resultados
def print_result(result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    print(f'Face landmarks detected at timestamp {timestamp_ms}ms')
    for face_landmark in result.face_landmarks:
        print(face_landmark)

# Opciones para el FaceLandmarker
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result
)

# Usar la webcam como entrada
with FaceLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)  # Abre la cámara web (usa el índice 0 por defecto)
    
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer un cuadro de video.")
            break
        
        # Convierte el cuadro a formato RGB para MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Crea un objeto `Image` de MediaPipe
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        # Calcula la marca de tiempo en milisegundos
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        
        # Procesa el cuadro con el landmarker
        landmarker.detect_async(mp_image, timestamp_ms)
        
        # Muestra el video en vivo
        cv2.imshow("Face Landmarker", frame)
        
        # Salir si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera los recursos
    cap.release()
    cv2.destroyAllWindows()
