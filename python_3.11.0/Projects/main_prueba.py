import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import cv2
from utils.camara_selector import seleccionar_camara_con_nombre
from config.config_manager import (
    cargar_config,
    obtener_usuario,
    crear_o_actualizar_usuario,
    guardar_ultimo_usuario,
    cargar_ultimo_usuario
)
from config.config_editor import ConfigEditor  # 👈 usamos el editor externo
from detector.face_detector_prueba import FaceDetectorPrueba
from controller.gesture_controller import GestureController
from logic.metrics import calculate_ear, calculate_mouth_openness,calculate_eyebrow_lift,calculate_roll_deg
from logic.metrics import calculate_ear, calculate_mouth_openness,calculate_eyebrow_lift,calculate_roll_deg, calculate_pitch_deg
from utils.constants import *
import mediapipe as mp
import time
from utils.preview_sensibilidades import mostrar_preview
import os, sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
GESTO_LABELS = {
            "left_eye": "Ojo izquierdo",
            "right_eye": "Ojo derecho",
            "mouth": "Boca",
            "eyebrows": "Cejas",  
            "roll_left": "Cabeza a la IZQUIERDA",
            "roll_right": "Cabeza a la DERECHA",   
}
class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Launcher")
        self.root.resizable(False, False)  # <-- Esto deshabilita el agrandado
        
        self.nombre_usuario = None
        self.gestos_config = None
        self.camera_index = None

        # Crear un frame horizontal para los botones y la imagen
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=30)

        # Frame para los botones (izquierda)
        btns_frame = tk.Frame(main_frame)
        btns_frame.pack(side="left", fill="y", anchor="center")
        tk.Button(btns_frame, text="Elegir Usuario", command=self.abrir_gestion_usuarios, width=30).pack(pady=20)
        tk.Button(btns_frame, text="Elegir Cámara", command=self.elegir_camara, width=30).pack(pady=20)
        tk.Button(btns_frame, text="Iniciar", command=self.iniciar, width=30).pack(pady=20)

        # Frame para la imagen (derecha)
        img_frame = tk.Frame(main_frame)
        img_frame.pack(side="left", fill="y", padx=20)
        img = Image.open(resource_path("img/yoshi.png"))
        img = img.resize((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        self.label_img = tk.Label(img_frame, image=img_tk)
        self.label_img.image = img_tk
        self.label_img.pack()
        
        # Centrar la ventana principal
        self.root.update_idletasks()  # Asegura que la ventana esté completamente creada
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def abrir_gestion_usuarios(self):
        """Ventana para seleccionar usuario y abrir el ConfigEditor externo."""
        win = tk.Toplevel(self.root)
        win.transient(self.root)
        win.grab_set()
        win.focus_set()
        win.title("Gestión de Usuarios")
        
        # Centrar la ventana
        win.update_idletasks()  # Asegura que la ventana esté completamente creada
        width = 400
        height = 200
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f'{width}x{height}+{x}+{y}')

        # UI: selector y botones
        lista_nombres = [u["nombre"] for u in cargar_config().get("usuarios", [])]
        selected_user = tk.StringVar()

        tk.Label(win, text="Seleccionar usuario:").pack(pady=5)
        user_menu = ttk.Combobox(win, textvariable=selected_user, values=lista_nombres, state="readonly", width=35)
        user_menu.pack(pady=5)

        btns = tk.Frame(win)
        btns.pack(pady=6)

        def refrescar_lista():
            nonlocal lista_nombres
            lista_nombres = [u["nombre"] for u in cargar_config().get("usuarios", [])]
            user_menu["values"] = lista_nombres
            if lista_nombres:
                user_menu.current(0)

        def abrir_editor():
            """Abre el editor externo en un Toplevel. Al cerrarlo, refresca."""
            ed = tk.Toplevel(win)
            ed.title("Editor de Configuración de Usuarios")
            ConfigEditor(ed)
            # cuando se cierre el editor, refrescar la lista
            def on_close():
                try:
                    refrescar_lista()
                finally:
                    ed.destroy()
            ed.protocol("WM_DELETE_WINDOW", on_close)

        def cargar_usuario():
            nombre = selected_user.get()
            if not nombre:
                messagebox.showerror("Error", "Seleccioná un usuario")
                return
            usuario = obtener_usuario(nombre)
            if not usuario or "gestos" not in usuario:
                messagebox.showerror("Error", f"El usuario '{nombre}' no tiene configuraciones de gestos.")
                return
            self.nombre_usuario = nombre
            self.gestos_config = usuario["gestos"]
            guardar_ultimo_usuario(nombre)
            messagebox.showinfo("OK", f"Usuario '{nombre}' seleccionado correctamente.")
            win.destroy()

        def cargar_ultimo():
            ultimo = cargar_ultimo_usuario()
            if not ultimo:
                messagebox.showinfo("Info", "No hay último usuario guardado.")
                return
            usuario = obtener_usuario(ultimo)
            if not usuario or "gestos" not in usuario:
                messagebox.showerror("Error", f"El último usuario '{ultimo}' no tiene configuraciones de gestos.")
                return
            self.nombre_usuario = ultimo
            self.gestos_config = usuario["gestos"]
            if ultimo in lista_nombres:
                selected_user.set(ultimo)
            messagebox.showinfo("OK", f"Se cargó el último usuario: {ultimo}")

        tk.Button(btns, text="Abrir editor (crear/editar)", command=abrir_editor).grid(row=0, column=0, padx=5)
        tk.Button(btns, text="Refrescar lista", command=refrescar_lista).grid(row=0, column=1, padx=5)
        tk.Button(btns, text="Cargar último usuario", command=cargar_ultimo).grid(row=0, column=2, padx=5)
        tk.Button(win, text="Usar seleccionado", command=cargar_usuario, width=30).pack(pady=10)

        # inicial
        if lista_nombres:
            user_menu.current(0)

    def elegir_camara(self):
        index = seleccionar_camara_con_nombre(self.root)
        if index is not None and index >= 0:
            self.camera_index = index
            messagebox.showinfo("Cámara seleccionada", f"Índice de cámara seleccionado: {self.camera_index}")

    def iniciar(self):
        if not self.nombre_usuario or not self.gestos_config:
            messagebox.showerror("Error", "Seleccioná un usuario primero")
            return
        if self.camera_index is None:
            messagebox.showerror("Error", "Seleccioná una cámara primero")
            return

        detector = FaceDetectorPrueba(camera_index=self.camera_index)
        controller = GestureController(self.gestos_config)
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles

        cv2.namedWindow("Frame")
        while True:
            start_time = time.time()
            frame, results = detector.get_frame_and_landmarks()
            if frame is None:
                break

            if results and results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    lm = face_landmarks.landmark
                    roll_deg = calculate_roll_deg(lm, LEFT_EYE, RIGHT_EYE, frame.shape)
                    pitch_deg = calculate_pitch_deg(lm, LEFT_EYE, RIGHT_EYE, frame.shape)
                    thr_roll_left  = self.gestos_config.get("roll_left",  {"threshold": ROLL_THRESHOLD_DEG})["threshold"]
                    thr_roll_right = self.gestos_config.get("roll_right", {"threshold": ROLL_THRESHOLD_DEG})["threshold"]

                    gestures = {}
                    for gesto in ["left_eye", "right_eye", "mouth", "roll_left", "roll_right", "pitch_up", "pitch_down"]:
                        conf = self.gestos_config.get(gesto, {})
                        if not conf.get("enabled", True):
                            gestures[gesto] = False
                        else:
                            if gesto == "left_eye":
                                gestures[gesto] = calculate_ear(lm, RIGHT_EYE) < conf["threshold"]
                            elif gesto == "right_eye":
                                gestures[gesto] = calculate_ear(lm, LEFT_EYE) < conf["threshold"]
                            elif gesto == "mouth":
                                gestures[gesto] = calculate_mouth_openness(lm, MOUTH) > conf["threshold"]
                            elif gesto == "roll_left":
                                gestures[gesto] = roll_deg > conf["threshold"]
                            elif gesto == "roll_right":
                                gestures[gesto] = roll_deg < -conf["threshold"]
                            elif gesto == "pitch_up":
                                gestures[gesto] = pitch_deg < conf["threshold"]
                            elif gesto == "pitch_down":
                                gestures[gesto] = pitch_deg > conf["threshold"]

                    # --- Cejas como UN gesto (promedio de izquierda + derecha) ---
                    left_lift  = calculate_eyebrow_lift(lm, EYEBROW_LEFT,  EYE_CENTER_LEFT)
                    right_lift = calculate_eyebrow_lift(lm, EYEBROW_RIGHT, EYE_CENTER_RIGHT)
                    eyebrow_conf = self.gestos_config.get("eyebrows", {"threshold": EYEBROW_THRESHOLD, "enabled": True})
                    if not eyebrow_conf.get("enabled", True):
                        gestures["eyebrows"] = False
                    else:
                        avg_lift = (left_lift + right_lift) / 2.0
                        gestures["eyebrows"] = avg_lift > eyebrow_conf["threshold"]

                    controller.update(gestures)
                    
                    mp_drawing.draw_landmarks(
                        frame, face_landmarks, mp.solutions.face_mesh.FACEMESH_CONTOURS, None,
                        mp_drawing_styles.get_default_face_mesh_contours_style())

                    mp_drawing.draw_landmarks(
                        frame, face_landmarks, mp.solutions.face_mesh.FACEMESH_IRISES, None,
                        mp_drawing_styles.get_default_face_mesh_iris_connections_style())

            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1)
            if key == -1 and cv2.getWindowProperty("Frame", cv2.WND_PROP_VISIBLE) <= 0:
                break
            elif key & 0xFF == ord('q'):
                break

        detector.release()
        controller.release_all()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
