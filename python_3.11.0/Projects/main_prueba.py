import tkinter as tk
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
from detector.face_detector_prueba import FaceDetectorPrueba
from controller.gesture_controller import GestureController
from logic.metrics import calculate_ear, calculate_mouth_openness
from utils.constants import *
import mediapipe as mp
import time
from utils.preview_sensibilidades import mostrar_preview

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Launcher")

        self.nombre_usuario = None
        self.gestos_config = None
        self.camera_index = None

        tk.Button(root, text="Elegir Usuario", command=self.abrir_gestion_usuarios, width=30).pack(pady=10)
        tk.Button(root, text="Elegir Cámara", command=self.elegir_camara, width=30).pack(pady=10)
        tk.Button(root, text="Iniciar", command=self.iniciar, width=30).pack(pady=10)

    def abrir_gestion_usuarios(self):
        win = tk.Toplevel(self.root)
        win.transient(self.root)
        win.grab_set()
        win.focus_set()
        win.title("Gestión de Usuarios")

        usuarios_config = cargar_config()
        usuarios_nombres = [u["nombre"] for u in usuarios_config["usuarios"]]
        selected_user = tk.StringVar()

        tk.Label(win, text="Seleccionar usuario:").pack(pady=5)
        user_menu = ttk.Combobox(win, textvariable=selected_user, values=usuarios_nombres, state="readonly")
        user_menu.pack(pady=5)

        frame_botones = tk.Frame(win)
        frame_botones.pack(pady=5)

        def cargar_usuario():
            nombre = selected_user.get()
            if not nombre:
                messagebox.showerror("Error", "Seleccioná un usuario")
                return
            usuario = obtener_usuario(nombre)
            if not usuario:
                messagebox.showerror("Error", "Usuario no encontrado")
                return
            if "gestos" not in usuario:
                messagebox.showerror("Error", f"El usuario '{nombre}' no tiene configuraciones de gestos.")
                return
            self.nombre_usuario = nombre
            self.gestos_config = usuario["gestos"]
            guardar_ultimo_usuario(nombre)
            messagebox.showinfo("OK", f"Usuario '{nombre}' seleccionado correctamente.")
            win.destroy()

        def nuevo_usuario():
            new_win = tk.Toplevel(win)
            new_win.transient(win)
            new_win.grab_set()
            new_win.focus_set()
            new_win.title("Nuevo Usuario")
            tk.Label(new_win, text="Nombre del nuevo usuario:").pack(pady=5)
            nombre_var = tk.StringVar()
            tk.Entry(new_win, textvariable=nombre_var).pack(pady=5)

            def crear():
                nombre = nombre_var.get().strip()
                if not nombre:
                    messagebox.showerror("Error", "Nombre vacío")
                    return
                if nombre in usuarios_nombres:
                    messagebox.showerror("Error", "Ese usuario ya existe")
                    return
                selected_user.set(nombre)
                usuarios_nombres.append(nombre)
                user_menu["values"] = usuarios_nombres
                crear_o_actualizar_usuario(nombre, {"left_eye": {}, "right_eye": {}, "mouth": {}})
                messagebox.showinfo("Usuario creado", f"Usuario '{nombre}' creado. Ahora configurá sus gestos.")
                new_win.destroy()

            tk.Button(new_win, text="Crear", command=crear).pack(pady=5)

        def editar_usuario():
            nombre = selected_user.get()
            if not nombre:
                messagebox.showerror("Error", "Seleccioná un usuario primero")
                return

            editor = tk.Toplevel(win)
            editor.transient(win)
            editor.grab_set()
            editor.focus_set()
            editor.title(f"Editar Gestos - {nombre}")
            gestos = ["left_eye", "right_eye", "mouth"]
            entries = {}
            teclas = {}
            user_data = obtener_usuario(nombre) or {"gestos": {}}

            for gesto in gestos:
                frame = tk.Frame(editor)
                frame.pack(pady=3)
                tk.Label(frame, text=gesto).grid(row=0, column=0)
                tk.Label(frame, text="Threshold:").grid(row=0, column=1)
                entries[gesto] = tk.Entry(frame, width=10)
                entries[gesto].grid(row=0, column=2)
                entries[gesto].insert(0, str(user_data["gestos"].get(gesto, {}).get("threshold", "")))
                tk.Label(frame, text="Tecla:").grid(row=0, column=3)
                teclas[gesto] = tk.Entry(frame, width=5)
                teclas[gesto].grid(row=0, column=4)
                teclas[gesto].insert(0, user_data["gestos"].get(gesto, {}).get("tecla", ""))

            def guardar():
                config = {}
                try:
                    for gesto in gestos:
                        threshold = float(entries[gesto].get())
                        tecla = teclas[gesto].get().strip()
                        if not tecla:
                            raise ValueError("Tecla vacía")
                        config[gesto] = {"threshold": threshold, "tecla": tecla}
                except ValueError:
                    messagebox.showerror("Error", "Valores inválidos")
                    return
                crear_o_actualizar_usuario(nombre, config)
                guardar_ultimo_usuario(nombre)
                messagebox.showinfo("Guardado", f"Configuración guardada para '{nombre}'")
                editor.destroy()
            tk.Button(editor, text="Ver sensibilidades", command=mostrar_preview).pack(pady=5)
            tk.Button(editor, text="Guardar", command=guardar).pack(pady=5)

        tk.Button(frame_botones, text="Usar", command=cargar_usuario).grid(row=0, column=0, padx=5)
        tk.Button(frame_botones, text="Nuevo", command=nuevo_usuario).grid(row=0, column=1, padx=5)
        tk.Button(frame_botones, text="Editar", command=editar_usuario).grid(row=0, column=2, padx=5)

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
                    gestures = {
                        'left_eye': calculate_ear(lm, LEFT_EYE) < self.gestos_config["left_eye"]["threshold"],
                        'right_eye': calculate_ear(lm, RIGHT_EYE) < self.gestos_config["right_eye"]["threshold"],
                        'mouth': calculate_mouth_openness(lm, MOUTH) < self.gestos_config["mouth"]["threshold"]
                    }
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
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
