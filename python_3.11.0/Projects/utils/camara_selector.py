import cv2
from pygrabber.dshow_graph import FilterGraph
import tkinter as tk
from tkinter import ttk, messagebox
import threading

def listar_camaras_con_nombre():
    graph = FilterGraph()
    return graph.get_input_devices()

class CameraSelectorApp:
    def __init__(self, parent):
        self.root = tk.Toplevel(parent)
        self.root.withdraw()  # Ocultar la ventana inicialmente
        self.root.title("Seleccionar Cámara")
        self.nombres = listar_camaras_con_nombre()
        self.selected_index = None
        self.preview_thread = None
        self.running_preview = False
        self.current_window_name = None

        # Combobox de cámaras
        self.combo = ttk.Combobox(self.root, values=self.nombres, state="readonly", width=60)
        self.combo.pack(padx=10, pady=10)

        # Botonera
        btns = tk.Frame(self.root)
        btns.pack(pady=8)

        self.preview_btn = tk.Button(btns, text="Previsualizar cámara", command=self.previsualizar)
        self.preview_btn.grid(row=0, column=0, padx=6)

        self.confirmar_btn = tk.Button(btns, text="Confirmar selección", command=self.confirmar)
        self.confirmar_btn.grid(row=0, column=1, padx=6)

        # Asegurar limpieza al cerrar con la X
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Centrar la ventana y mostrarla
        self.root.update_idletasks()  # Asegura que la ventana esté completamente creada
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()  # Mostrar la ventana ya centrada

    # ------ Acciones de UI ------

    def previsualizar(self):
        idx = self.combo.current()
        if idx == -1:
            messagebox.showinfo("Info", "Elegí una cámara del listado para previsualizar.")
            return
        # Cierra preview anterior si existe
        self._stop_preview_if_running()
        # Inicia uno nuevo
        self.preview_thread = threading.Thread(target=self._preview_camera, args=(idx,), daemon=True)
        self.preview_thread.start()

    def confirmar(self):
        self.selected_index = self.combo.current()
        if self.selected_index == -1:
            messagebox.showerror("Error", "Seleccioná una cámara antes de confirmar.")
            return
        self._stop_preview_if_running()
        self.root.destroy()

    # ------ Preview ------

    def _preview_camera(self, idx):
        self.running_preview = True
        cap = cv2.VideoCapture(idx)
        if not cap.isOpened():
            messagebox.showerror("Error", f"No se pudo abrir la cámara {idx}")
            self.running_preview = False
            return

        self.current_window_name = f"Preview - {self.nombres[idx]}"
        cv2.namedWindow(self.current_window_name)

        while self.running_preview:
            ret, frame = cap.read()

            # Si falla la captura o el usuario cerró la ventana, salimos
            if not ret or cv2.getWindowProperty(self.current_window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

            cv2.imshow(self.current_window_name, frame)

            # Permitir cerrar con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.running_preview = False
        cap.release()
        # Destruir ventana si sigue abierta
        try:
            cv2.destroyWindow(self.current_window_name)
        except cv2.error:
            pass
        self.current_window_name = None

    def _stop_preview_if_running(self):
        if self.running_preview:
            self.running_preview = False
        if self.preview_thread and self.preview_thread.is_alive():
            self.preview_thread.join(timeout=1.0)
        # Por si quedó una ventana colgada
        if self.current_window_name:
            try:
                cv2.destroyWindow(self.current_window_name)
            except cv2.error:
                pass
            self.current_window_name = None

    # ------ Cierre seguro de la ventana ------

    def _on_close(self):
        self._stop_preview_if_running()
        self.root.destroy()


def seleccionar_camara_con_nombre(parent=None):
    app = CameraSelectorApp(parent)
    app.root.transient(parent)   # opcional pero elegante
    app.root.grab_set()          # bloquea interacción con el padre
    app.root.focus_set()         # lleva el foco al selector
    app.root.wait_window()       # espera hasta que el usuario la cierre
    return app.selected_index
