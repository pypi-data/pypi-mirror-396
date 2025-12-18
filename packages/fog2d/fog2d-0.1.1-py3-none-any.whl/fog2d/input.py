try:
    import msvcrt
    def default_get_key():
        if msvcrt.kbhit():
            return msvcrt.getch().decode().lower()
        return None
except ImportError:
    def default_get_key():
        return None

class InputSystem:
    def __init__(self):
        self.pressed = set()

    def update(self):
        key = default_get_key()
        if key:
            self.pressed.add(key)

    def is_pressed(self, key):
        return key in self.pressed

    def clear(self):
        self.pressed.clear()
