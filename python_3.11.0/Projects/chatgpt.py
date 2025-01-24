import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Ruta al modelo pre-entrenado
model_path = "face_landmarker.task"

# Importar componentes necesarios
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
DrawingUtils = mp.solutions.drawing_utils

# Función para dibujar puntos y contornos faciales
def draw_landmarks(result: FaceLandmarkerResult, frame):
    """Dibuja los puntos y contornos faciales en el cuadro del video."""
    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            DrawingUtils.draw_landmarks(
                frame,
                face_landmarks,
                mp.solutions.face_mesh.FACEMESH_TESSELATION,  # Dibuja la malla facial
                DrawingUtils.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),  # Estilo de puntos
                DrawingUtils.DrawingSpec(color=(255, 0, 0), thickness=1)  # Estilo de líneas
            )

# Callback para manejar los resultados
def process_result(result: FaceLandmarkerResult, frame, output_image, timestamp_ms):
    """Procesa y dibuja los resultados en el cuadro."""
    draw_landmarks(result, frame)

# Opciones para el FaceLandmarker
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=lambda result, output_image, timestamp_ms: process_result(
        result, frame, output_image, timestamp_ms
    )
)

# Inicializar y usar la cámara
try:
    with FaceLandmarker.create_from_options(options) as landmarker:
        cap = cv2.VideoCapture(0)  # Índice de la cámara (0 para la principal)

        if not cap.isOpened():
            print("Error: No se pudo abrir la cámara.")
            exit()

        # Reducir la resolución del video
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Ancho
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Alto

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
            
            # Procesa el cuadro con el landmarker en modo LIVE_STREAM
            landmarker.detect_async(mp_image, timestamp_ms)
            
            # Muestra el video en vivo
            cv2.imshow("Face Landmarker", frame)
            
            # Salir si se presiona la tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Libera los recursos
        cap.release()
        cv2.destroyAllWindows()
except Exception as e:
    print(f"Error al procesar el modelo: {e}")
