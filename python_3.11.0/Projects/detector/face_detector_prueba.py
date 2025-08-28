import cv2
import mediapipe as mp

class FaceDetectorPrueba:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

    def get_frame_and_landmarks(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        return frame, results

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

