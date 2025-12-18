import sys
from colorama import Style

WIDTH, HEIGHT = 40, 20

class Renderer:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.front = {}
        self.back = {}

    def draw(self, x, y, ch, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.back[(x, y)] = (ch, color)

    def present(self):
        for pos in self.front:
            if pos not in self.back:
                self._draw_at(pos[0], pos[1], " ", "")

        for pos, (ch, color) in self.back.items():
            if self.front.get(pos) != (ch, color):
                self._draw_at(pos[0], pos[1], ch, color)

        self.front = self.back.copy()
        self.back.clear()
        sys.stdout.flush()

    def _draw_at(self, x, y, ch, color):
        sys.stdout.write(f"\033[{y+1};{x+1}H{color}{ch}{Style.RESET_ALL}")