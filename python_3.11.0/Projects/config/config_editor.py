import tkinter as tk
from tkinter import messagebox, ttk
from config_manager import (
    cargar_config,
    obtener_usuario,
    crear_o_actualizar_usuario,
    guardar_ultimo_usuario,
)

class ConfigEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Seleccionar o Crear Usuario")

        self.usuarios_config = cargar_config()
        self.usuarios_nombres = [u["nombre"] for u in self.usuarios_config["usuarios"]]
        self.selected_user = tk.StringVar()

        # Menú de selección
        tk.Label(root, text="Seleccionar usuario:").pack(pady=5)
        self.user_menu = ttk.Combobox(root, textvariable=self.selected_user, values=self.usuarios_nombres, state="readonly")
        self.user_menu.pack()

        # Botones
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Usar", command=self.cargar_usuario).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Nuevo usuario", command=self.nuevo_usuario).grid(row=0, column=1, padx=5)

        # Edición de gestos
        self.edit_frame = tk.Frame(root)
        self.entries = {}
        self.teclas = {}
        self.gestos = ["left_eye", "right_eye", "mouth"]

        for gesto in self.gestos:
            row = tk.Frame(self.edit_frame)
            row.pack(pady=3)

            tk.Label(row, text=f"{gesto}").grid(row=0, column=0, padx=5)
            tk.Label(row, text="Threshold:").grid(row=0, column=1)
            self.entries[gesto] = tk.Entry(row, width=10)
            self.entries[gesto].grid(row=0, column=2)

            tk.Label(row, text="Tecla:").grid(row=0, column=3)
            self.teclas[gesto] = tk.Entry(row, width=5)
            self.teclas[gesto].grid(row=0, column=4)

        self.save_btn = tk.Button(root, text="Guardar configuración", command=self.guardar_config)
        self.edit_frame.pack(pady=10)
        self.save_btn.pack()

        # Ocultar editor hasta que se seleccione usuario
        self.edit_frame.pack_forget()
        self.save_btn.pack_forget()

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
            self.entries[gesto].delete(0, tk.END)
            self.entries[gesto].insert(0, str(conf.get("threshold", "")))
            self.teclas[gesto].delete(0, tk.END)
            self.teclas[gesto].insert(0, conf.get("tecla", ""))

        self.edit_frame.pack()
        self.save_btn.pack()
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
            self.save_btn.pack()
            # Vaciar campos
            for gesto in self.gestos:
                self.entries[gesto].delete(0, tk.END)
                self.teclas[gesto].delete(0, tk.END)

        tk.Button(new_window, text="Crear", command=crear).pack(pady=5)

    def guardar_config(self):
        nombre = self.selected_user.get()
        config = {}
        try:
            for gesto in self.gestos:
                threshold = float(self.entries[gesto].get())
                tecla = self.teclas[gesto].get().strip()
                if not tecla:
                    raise ValueError("Tecla vacía")
                config[gesto] = {"threshold": threshold, "tecla": tecla}
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos.")
            return

        crear_o_actualizar_usuario(nombre, config)
        guardar_ultimo_usuario(nombre)
        messagebox.showinfo("Guardado", f"Configuración guardada para '{nombre}'")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
