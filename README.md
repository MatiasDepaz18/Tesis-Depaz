# 💻 Mi Proyecto Python

Este proyecto fue desarrollado en Python 3.11.0 utilizando un entorno virtual manejado con `pyenv`. A continuación se explican los pasos para instalar y ejecutar el proyecto desde cero tanto en **Windows** como en **macOS**.

---

## 🚀 Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/usuario/mi-proyecto.git
cd mi-proyecto
```

> Reemplazá la URL por la real de tu repositorio.

---

## 🪟 Instalación en Windows

### 2. Instalar Git

- Descargar desde: https://git-scm.com/downloads
- Durante la instalación, elegir la opción: `Git from the command line and also from 3rd-party software`.

### 3. Instalar pyenv para Windows (pyenv-win)

Abrí PowerShell como **Administrador** y ejecutá:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri https://pyenv.run -OutFile pyenv-installer.bat
.\pyenv-installer.bat
```

Cerrá y volvé a abrir PowerShell. Verificá la instalación:

```powershell
pyenv --version
```

> Si no funciona, reiniciá la computadora o revisá las variables de entorno (PATH).

### 4. Instalar Python 3.11.0 y crear entorno virtual

```powershell
pyenv install 3.11.0
pyenv virtualenv 3.11.0 mi-entorno
pyenv local mi-entorno
```

---

## 🍏 Instalación en macOS

### 2. Instalar Homebrew (si no lo tenés)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Agregar Homebrew al PATH (según tu Mac):

**Apple Silicon:**

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
source ~/.zprofile
```

**Intel:**

```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
source ~/.zprofile
```

### 3. Instalar pyenv y pyenv-virtualenv

```bash
brew install pyenv pyenv-virtualenv
```

Agregar a tu `.zshrc`:

```bash
echo -e '\n# Pyenv setup' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
source ~/.zshrc
```

### 4. Instalar Python 3.11.0 y crear entorno virtual

```bash
pyenv install 3.11.0
pyenv virtualenv 3.11.0 mi-entorno
pyenv local mi-entorno
```

---

## 📦 Instalar dependencias del proyecto (común a ambos)

Con el entorno virtual activado (tras `pyenv local`):

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecutar el proyecto

```bash
python main.py
```

> Reemplazá `main.py` por el nombre del archivo principal de tu proyecto si es distinto.

---

## 📁 Estructura del proyecto

```
mi-proyecto/
├── main.py
├── requirements.txt
├── README.md
└── ...
```

---

## ❓ Tips

- Verificá la versión activa de Python con:

  ```bash
  python --version
  which python  # en macOS
  where python  # en Windows
  ```

- En macOS, si usás `bash`, agregá las líneas a `~/.bashrc` o `~/.bash_profile` en vez de `~/.zshrc`.

---

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](LICENSE) (o la que elijas).
