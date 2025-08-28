import cv2
from pygrabber.dshow_graph import FilterGraph
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading

def listar_camaras_con_nombre():
    graph = FilterGraph()
    return graph.get_input_devices()

class CameraSelectorApp:
    def __init__(self,parent):
        self.root = tk.Toplevel(parent)
        self.root.title("Seleccionar Cámara")
        self.nombres = listar_camaras_con_nombre()
        self.selected_index = None
        self.preview_thread = None
        self.running_preview = False

        # Combobox de cámaras
        self.combo = ttk.Combobox(self.root, values=self.nombres, state="readonly", width=60)
        self.combo.pack(padx=10, pady=10)
        self.combo.bind("<<ComboboxSelected>>", self.on_camera_select)

        # Botón para confirmar
        self.confirmar_btn = tk.Button(self.root, text="Confirmar selección", command=self.confirmar)
        self.confirmar_btn.pack(pady=10)

    def on_camera_select(self, event=None):
        idx = self.combo.current()
        if idx != -1:
            # Cierra preview anterior si hay uno abierto
            self.running_preview = False
            if self.preview_thread and self.preview_thread.is_alive():
                self.preview_thread.join()
            # Abre nuevo preview
            self.preview_thread = threading.Thread(target=self.preview_camera, args=(idx,))
            self.preview_thread.start()

    def preview_camera(self, idx):
        self.running_preview = True
        cap = cv2.VideoCapture(idx)
        if not cap.isOpened():
            print(f"No se pudo abrir la cámara {idx}")
            return

        window_name = f"Preview - {self.nombres[idx]}"
        cv2.namedWindow(window_name)

        while self.running_preview:
            ret, frame = cap.read()

            # Verificar si la ventana fue cerrada manualmente
            if not ret or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("Preview cerrado por el usuario (botón X o error de captura)")
                break

            cv2.imshow(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.running_preview = False
        cap.release()

        # Intentar destruir, pero atrapar el error si la ventana ya no existe
        try:
            cv2.destroyWindow(window_name)
        except cv2.error as e:
            print(f"(Info) La ventana ya fue cerrada: {e}")

    def confirmar(self):
        self.selected_index = self.combo.current()
        self.running_preview = False
        if self.preview_thread and self.preview_thread.is_alive():
            self.preview_thread.join()
        self.root.destroy()

def seleccionar_camara_con_nombre(parent=None):
    app = CameraSelectorApp(parent)
    app.root.transient(parent)   # opcional pero elegante
    app.root.grab_set()          # bloquea interacción con el padre
    app.root.focus_set()         # lleva el foco al selector
    app.root.wait_window()       # espera hasta que el usuario la cierre
    return app.selected_index