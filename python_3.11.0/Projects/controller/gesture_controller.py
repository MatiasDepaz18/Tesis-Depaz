from pynput import keyboard

_SPECIALS = {
    "SPACE": keyboard.Key.space,
    "ENTER": keyboard.Key.enter,
    "RETURN": keyboard.Key.enter,
    "TAB": keyboard.Key.tab,
    "BACKSPACE": keyboard.Key.backspace,
    "ESC": keyboard.Key.esc,
    "ESCAPE": keyboard.Key.esc,
    "UP": keyboard.Key.up,
    "DOWN": keyboard.Key.down,
    "LEFT": keyboard.Key.left,
    "RIGHT": keyboard.Key.right,
    "DELETE": keyboard.Key.delete,
    "INSERT": keyboard.Key.insert,
    "HOME": keyboard.Key.home,
    "END": keyboard.Key.end,
    "PAGE_UP": keyboard.Key.page_up,
    "PAGE_DOWN": keyboard.Key.page_down,
    "CAPS_LOCK": keyboard.Key.caps_lock,
    "NUM_LOCK": keyboard.Key.num_lock,
    "SCROLL_LOCK": keyboard.Key.scroll_lock,
    "PRINT_SCREEN": keyboard.Key.print_screen,
    "MENU": keyboard.Key.menu,
    "PAUSE": keyboard.Key.pause,
}

def _to_key(label: str):
    if not label:
        return None
    s = str(label).strip()
    if s.lower().startswith("key."):
        s = s[4:]
    su = s.upper()
    if su.startswith("F") and su[1:].isdigit():
        attr = f"f{su[1:]}"
        if hasattr(keyboard.Key, attr):
            return getattr(keyboard.Key, attr)
    if su in _SPECIALS:
        return _SPECIALS[su]
    if len(s) == 1:
        return keyboard.KeyCode.from_char(s.lower())
    for k, v in _SPECIALS.items():
        if k.lower() == s.lower():
            return v
    return None

class GestureController:
    def __init__(self, gestos_config: dict):
        """
        gestos_config = {
          "left_eye": {"threshold": 0.22, "tecla": "A"},
          "right_eye": {"threshold": 0.22, "tecla": "D"},
          "mouth": {"threshold": 0.06, "tecla": "W"},
          "eyebrows": {"threshold": 0.30, "tecla": "SPACE"},
          "roll_left": {"threshold": 12.0, "tecla": "Q"},
          "roll_right":{"threshold": 12.0, "tecla": "E"},
        }
        """
        self.config = gestos_config
        self.keyboard = keyboard.Controller()
        self.prev = {}          # estado anterior por gesto (bool)
        self._down_keys = {}    # gesto -> Key/KeyCode actualmente presionada

    def _keydown(self, gesture: str):
        label = self.config.get(gesture, {}).get("tecla")
        key_obj = _to_key(label)
        print(key_obj)
        if not key_obj:
            return
        if gesture in self._down_keys:
            return  # ya está abajo
        self.keyboard.press(key_obj)
        self._down_keys[gesture] = key_obj

    def _keyup(self, gesture: str):
        key_obj = self._down_keys.pop(gesture, None)
        if not key_obj:
            return
        self.keyboard.release(key_obj)

    def update(self, gestures: dict[str, bool]):
        """
        Mantiene la tecla mientras el gesto esté True; suelta al pasar a False.
        """
        for g, active in gestures.items():
            was = self.prev.get(g, False)
            if active and not was:
                self._keydown(g)
            elif (not active) and was:
                self._keyup(g)
        self.prev = gestures.copy()

    def release_all(self):
        for g in list(self._down_keys.keys()):
            self._keyup(g)
