import json
import os
import sys
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        # Si está empaquetado con PyInstaller
        return sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
    else:
        # Si está corriendo desde .py normal
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
LAST_USER_PATH = os.path.join(BASE_DIR, "last_user.json")

def cargar_config():
    if not os.path.exists(CONFIG_PATH):
        return {"usuarios": []}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def guardar_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def obtener_usuario(nombre):
    config = cargar_config()
    for user in config["usuarios"]:
        if user["nombre"] == nombre:
            return user
    return None

def crear_o_actualizar_usuario(nombre, gestos_config):
    config = cargar_config()
    for user in config["usuarios"]:
        if user["nombre"] == nombre:
            user["gestos"] = gestos_config
            guardar_config(config)
            return
    # Nuevo usuario
    config["usuarios"].append({"nombre": nombre, "gestos": gestos_config})
    guardar_config(config)

def guardar_ultimo_usuario(nombre):
    with open(LAST_USER_PATH, "w") as f:
        json.dump({"ultimo_usuario": nombre}, f)

def cargar_ultimo_usuario():
    if not os.path.exists(LAST_USER_PATH):
        print(os.path.exists(LAST_USER_PATH))
        return None
    with open(LAST_USER_PATH, "r") as f:
        data = json.load(f)
        return data.get("ultimo_usuario")
