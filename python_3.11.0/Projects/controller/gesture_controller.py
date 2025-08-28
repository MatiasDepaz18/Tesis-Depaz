from pynput.keyboard import Controller

class GestureController:
    def __init__(self, config):
        self.keyboard = Controller()
        self.left_eye_pressed = False
        self.right_eye_pressed = False
        self.mouth_pressed = False
        self.config = config  # Diccionario con teclas por gesto

    def update(self, gestures):
        if gestures['left_eye'] and not self.left_eye_pressed:
            self.keyboard.press(self.config["left_eye"]["tecla"])
            self.left_eye_pressed = True
        elif not gestures['left_eye'] and self.left_eye_pressed:
            self.keyboard.release(self.config["left_eye"]["tecla"])
            self.left_eye_pressed = False

        if gestures['right_eye'] and not self.right_eye_pressed:
            self.keyboard.press(self.config["right_eye"]["tecla"])
            self.right_eye_pressed = True
        elif not gestures['right_eye'] and self.right_eye_pressed:
            self.keyboard.release(self.config["right_eye"]["tecla"])
            self.right_eye_pressed = False

        if gestures['mouth'] and not self.mouth_pressed:
            self.keyboard.press(self.config["mouth"]["tecla"])
            self.mouth_pressed = True
        elif not gestures['mouth'] and self.mouth_pressed:
            self.keyboard.release(self.config["mouth"]["tecla"])
            self.mouth_pressed = False
