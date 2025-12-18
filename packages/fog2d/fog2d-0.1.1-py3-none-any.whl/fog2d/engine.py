import time
from colorama import Fore, Style
from .renderer import Renderer
from .scene import Scene
from .input import InputSystem
from .utils import clear, cursor

FPS = 30

def splash():
    clear()
    logo = [
        "███████╗ ██████╗  ██████╗ ██████╗ ██████╗ ",
        "██╔════╝██╔═══██╗██╔════╝╚════██╗██╔══██╗",
        "█████╗  ██║   ██║██║  ███╗ █████╔╝██║  ██║",
        "██╔══╝  ██║   ██║██║   ██║██╔═══╝ ██║  ██║",
        "██║     ╚██████╔╝╚██████╔╝███████╗██████╔╝",
        "╚═╝      ╚═════╝  ╚═════╝ ╚══════╝╚═════╝ ",
        "",
        "Fog2D Engine"
    ]
    y = 8
    for line in logo:
        cursor(5, y)
        print(Fore.WHITE + Style.BRIGHT + line)
        y += 1
    time.sleep(2)
    clear()

class Fog2D:
    def __init__(self):
        splash()
        self.renderer = Renderer()
        self.scene = Scene(self.renderer)
        self.input = InputSystem()
        clear()

    def run(self):
        while True:
            self.input.update()
            self.scene.update()
            self.scene.render()
            self.renderer.present()
            self.input.clear()
            time.sleep(1 / FPS)
