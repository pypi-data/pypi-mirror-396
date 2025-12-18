try:
    import msvcrt

    def default_get_key():
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            try:
                return ch.decode("utf-8").lower()
            except UnicodeDecodeError:
                return None
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
        return key.lower() in self.pressed

    def clear(self):
        self.pressed.clear()
