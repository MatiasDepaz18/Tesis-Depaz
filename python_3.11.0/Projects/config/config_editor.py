import tkinter as tk
from tkinter import messagebox, ttk
from threading import Thread
from pynput import keyboard  # para capturar la próxima tecla
from utils.preview_sensibilidades import mostrar_preview
from config.config_manager import (
    cargar_config,
    obtener_usuario,
    crear_o_actualizar_usuario,
    guardar_ultimo_usuario,
)

PLACEHOLDER = "Elegir tecla"
LISTENING   = "Escuchando… (ESC cancela)"
GESTO_LABELS = {
    "left_eye": "Ojo izquierdo",
    "right_eye": "Ojo derecho",
    "mouth": "Boca",
    "eyebrows": "Cejas",
    "roll_left": "Cabeza a la IZQUIERDA",
    "roll_right": "Cabeza a la DERECHA",
    "pitch_up": "Cabeza ARRIBA",
    "pitch_down": "Cabeza ABAJO",
}

class ConfigEditor:
    # Factores de escala para cada gesto
    GESTO_FACTORES = {
        "left_eye": 0.01,
        "right_eye": 0.01,
        "mouth": 0.001,
        "eyebrows": 0.001,
        "roll_left": 0.12,
        "roll_right": 0.12,
        "pitch_up": 1,
        "pitch_down": 1,
    }
    def __init__(self, root):
        self.root = root
        self.root.title("Seleccionar o Crear Usuario")
        
        # Establecer tamaño mínimo para que siempre aparezca grande
        self.root.minsize(700, 600)
        
        self.usuarios_config = cargar_config()
        self.usuarios_nombres = [u["nombre"] for u in self.usuarios_config["usuarios"]]
        self.selected_user = tk.StringVar()

        # Menú de selección
        tk.Label(root, text="Seleccionar usuario:").pack(pady=5)
        self.user_menu = ttk.Combobox(
            root,
            textvariable=self.selected_user,
            values=self.usuarios_nombres,
            state="readonly",
        )
        self.user_menu.pack()

        # Botones principales
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Usar", command=self.cargar_usuario).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Nuevo usuario", command=self.nuevo_usuario).grid(row=0, column=1, padx=5)
        tk.Scrollbar

        # Edición de gestos
        self.edit_frame = tk.Frame(root)
        self.action_frame = tk.Frame(root)
        self.save_btn = tk.Button(self.action_frame, text="Guardar configuración", command=self.guardar_config)
        self.preview_btn = tk.Button(self.action_frame, text="Preview Sensibilidades", command=self.preview_sensibilidades)
        self.save_btn.pack(side="left", padx=5)
        self.preview_btn.pack(side="left", padx=5)

        self.entries = {}   # thresholds (Entry)
        self.botones = {}   # teclas (Button)
        self.enabled_vars = {} # enabled (Checkbutton)
        self.gestos = ["left_eye", "right_eye", "mouth","eyebrows","roll_left", "roll_right","pitch_up","pitch_down"]

        for gesto in self.gestos:
            row = tk.Frame(self.edit_frame)
            row.pack(pady=3, fill="x")

            tk.Label(row, text=GESTO_LABELS.get(gesto, gesto),anchor='center',width=16).grid(row=0, column=0, padx=10, sticky="ew")

            if gesto in ["roll_left", "roll_right"]:
                tk.Label(row, text="Angulo Inclinacion:", anchor="center", width=15).grid(row=0, column=1, sticky="ew")
                self.entries[gesto] = tk.Scale(row, from_=9, to=15, orient=tk.HORIZONTAL, length=120, resolution=0.01)
            elif gesto in ["pitch_up"]:
                tk.Label(row, text="Angulo Inclinacion:", anchor="center", width=15).grid(row=0, column=1, sticky="ew")
                self.entries[gesto] = tk.Scale(row, from_=10, to=25, orient=tk.HORIZONTAL, length=120, resolution=0.01)
            elif gesto in ["pitch_down"]:
                tk.Label(row, text="Angulo Inclinacion:", anchor="center", width=15).grid(row=0, column=1, sticky="ew")
                self.entries[gesto] = tk.Scale(row, from_=30, to=40, orient=tk.HORIZONTAL, length=120, resolution=0.01)
            else:
                tk.Label(row, text="Threshold:", anchor="center", width=15).grid(row=0, column=1, sticky="ew")
                self.entries[gesto] = tk.Scale(row, from_=0, to=100, orient=tk.HORIZONTAL, length=120)
            self.entries[gesto].grid(row=0, column=2)

            tk.Label(row, text="Tecla:", anchor="center", width=8).grid(row=0, column=3, sticky="ew")

            # Botón que muestra la tecla actual y, al hacer click, captura la próxima
            btn = tk.Button(
                row,
                text=PLACEHOLDER,
                width=18,
                command=lambda g=gesto: self._lanzar_captura(g)
            )
            btn.grid(row=0, column=4, padx=4)
            self.botones[gesto] = btn

            # Checkbox para habilitar/deshabilitar gesto
            var_enabled = tk.BooleanVar(value=True)
            self.enabled_vars[gesto] = var_enabled
            chk = tk.Checkbutton(row, text="Habilitado", variable=var_enabled)
            chk.grid(row=0, column=5, padx=6)

        # Inicialmente oculto
        self.action_frame.pack_forget()
        self.edit_frame.pack_forget()

    # ---------- Captura de tecla ----------
    def preview_sensibilidades(self):
        valores = {gesto: self.entries[gesto].get() for gesto in self.gestos}
        # Llama a la función de preview y pásale los valores
        from utils.preview_sensibilidades import mostrar_preview
        mostrar_preview(valores)

    def _lanzar_captura(self, gesto: str):
        """Pone el botón en modo 'escuchando' y captura la próxima tecla en un hilo."""
        btn = self.botones[gesto]
        btn.config(text=LISTENING)

        def worker():
            label = self._capturar_una_tecla()  # bloquea solo este hilo
            # aplicar en el hilo principal
            def aplicar():
                if label:
                    btn.config(text=label)
                else:
                    # cancelado con ESC ⇒ volver a placeholder
                    btn.config(text=PLACEHOLDER)
            self.root.after(0, aplicar)

        Thread(target=worker, daemon=True).start()

    @staticmethod
    def _formatear_tecla(k) -> str:
        """Pasa la tecla a una etiqueta amigable: 'A', '1', 'SPACE', 'ENTER', 'LEFT'..."""
        # si es imprimible
        try:
            if hasattr(k, "char") and k.char:
                return k.char.upper()
        except Exception:
            pass
        # especiales
        return str(k).replace("Key.", "").upper()

    def _capturar_una_tecla(self) -> str | None:
        """Escucha una única tecla. ESC cancela y retorna None."""
        capturada = {"val": None}

        def on_press(k):
            # ESC cancela
            if k == keyboard.Key.esc:
                capturada["val"] = None
                return False
            capturada["val"] = self._formatear_tecla(k)
            return False  # terminar listener

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
        return capturada["val"]

    # ---------- Flujo UI ----------

    def cargar_usuario(self):
        nombre = self.selected_user.get()
        if not nombre:
            messagebox.showerror("Error", "Seleccioná un usuario.")
            return

        usuario = obtener_usuario(nombre)
        if not usuario:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return

        for gesto in self.gestos:
            conf = usuario["gestos"].get(gesto, {})
            # threshold
            valor_real = conf.get("threshold", 0)
            if gesto in ["roll_left", "roll_right"]:
                self.entries[gesto].set(valor_real)
            else:
                factor = self.GESTO_FACTORES.get(gesto, 1)
                valor_visual = int(round(valor_real / factor))
                self.entries[gesto].set(valor_visual)
            # tecla como texto del botón
            tecla = conf.get("tecla", "").strip()
            self.botones[gesto].config(text=tecla if tecla else PLACEHOLDER)
            # habilitado
            self.enabled_vars[gesto].set(conf.get("enabled", True))

        self.edit_frame.pack()
        self.action_frame.pack(pady=10)
        
        # Recentrar la ventana después de expandirse
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        guardar_ultimo_usuario(nombre)

    def nuevo_usuario(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Crear nuevo usuario")
        tk.Label(new_window, text="Nombre del nuevo usuario:").pack(pady=5)
        nombre_var = tk.StringVar()
        tk.Entry(new_window, textvariable=nombre_var).pack(pady=5)

        def crear():
            nombre = nombre_var.get().strip()
            if not nombre:
                messagebox.showerror("Error", "Nombre vacío.")
                return
            if nombre in self.usuarios_nombres:
                messagebox.showerror("Error", "El usuario ya existe.")
                return

            self.selected_user.set(nombre)
            self.usuarios_nombres.append(nombre)
            self.user_menu["values"] = self.usuarios_nombres
            new_window.destroy()
            self.edit_frame.pack()
            self.action_frame.pack(pady=10)
            
            # Recentrar la ventana después de expandirse
            self.root.update_idletasks()
            width = self.root.winfo_reqwidth()
            height = self.root.winfo_reqheight()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
            
            # limpiar campos
            for gesto in self.gestos:
                if gesto in ["roll_left", "roll_right"]:
                    self.entries[gesto].set(12)
                else:
                    self.entries[gesto].set(0)
                self.botones[gesto].config(text=PLACEHOLDER)
                self.enabled_vars[gesto].set(True)
        tk.Button(new_window, text="Crear", command=crear).pack(pady=5)

    def guardar_config(self):
        nombre = self.selected_user.get()
        if not nombre:
            messagebox.showerror("Error", "Seleccioná un usuario.")
            return

        config = {}
        try:
            usadas = set()
            for gesto in self.gestos:
                # threshold
                valor_visual = self.entries[gesto].get()
                if gesto in ["roll_left", "roll_right"]:
                    threshold = float(valor_visual)
                else:
                    factor = self.GESTO_FACTORES.get(gesto, 1)
                    threshold = float(valor_visual) * factor
                # tecla desde el botón
                label = self.botones[gesto].cget("text").strip()

                # habilitado
                enabled = self.enabled_vars[gesto].get()

                if not label or label == PLACEHOLDER or label == LISTENING:
                    raise ValueError(f"Tecla no definida en '{gesto}'")

                up = label.upper()
                if up in usadas:
                    raise ValueError(f"La tecla '{label}' está repetida entre gestos")
                usadas.add(up)

                config[gesto] = {"threshold": threshold, "tecla": label, "enabled": enabled}
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")
            return

        crear_o_actualizar_usuario(nombre, config)
        guardar_ultimo_usuario(nombre)
        messagebox.showinfo("Guardado", f"Configuración guardada para '{nombre}'")
        try:
            self.root.destroy()
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
