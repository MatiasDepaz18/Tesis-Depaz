from pynput.keyboard import Controller

class GestureController:
    def __init__(self):
        self.keyboard = Controller()
        self.left_eye_pressed = False
        self.right_eye_pressed = False
        self.mouse_pressed = False

    def update(self, gestures):
        if gestures['left_eye'] and not self.left_eye_pressed:
            self.keyboard.press('d')
            self.left_eye_pressed = True
        elif not gestures['left_eye'] and self.left_eye_pressed:
            self.keyboard.release('d')
            self.left_eye_pressed = False

        if gestures['right_eye'] and not self.right_eye_pressed:
            self.keyboard.press('a')
            self.right_eye_pressed = True
        elif not gestures['right_eye'] and self.right_eye_pressed:
            self.keyboard.release('a')
            self.right_eye_pressed = False

        if gestures['mouth'] and not self.mouse_pressed:
            self.keyboard.release('w')
            self.mouse_pressed = True
        elif not gestures['mouth'] and self.mouse_pressed:
            self.keyboard.press('w')
            self.mouse_pressed = False