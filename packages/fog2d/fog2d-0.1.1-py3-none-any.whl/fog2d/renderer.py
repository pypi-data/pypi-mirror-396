import sys
from colorama import Style
from .utils import cursor

WIDTH, HEIGHT = 40, 20

class Renderer:
    def __init__(self):
        self.front = {}
        self.back = {}

    def draw(self, x, y, ch, color):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self.back[(x, y)] = (ch, color)

    def present(self):
        for pos, data in self.back.items():
            if self.front.get(pos) != data:
                cursor(pos[0], pos[1])
                sys.stdout.write(data[1] + data[0] + Style.RESET_ALL)
        self.front = self.back.copy()
        self.back.clear()
        sys.stdout.flush()
