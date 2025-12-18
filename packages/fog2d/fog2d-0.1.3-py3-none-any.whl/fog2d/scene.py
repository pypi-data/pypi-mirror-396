from colorama import Back
from .collision import CollisionSystem
from .lighting import LightSystem

class Scene:
    def __init__(self, renderer):
        self.renderer = renderer
        self.entities = []
        self.light_system = LightSystem()

    def add(self, entity):
        self.entities.append(entity)

    def update(self):
        for e in self.entities:
            e.prev_x, e.prev_y = e.x, e.y

    def render(self):
        lights = [(e.light, e.x, e.y) for e in self.entities if e.light]

        for e in self.entities:
            brightness = self.light_system.light_at(e.x, e.y, lights)
            color = e.color
            if brightness < 0.2:
                color = "\033[40m"
            elif brightness < 0.5:
                color = "\033[44m"
            self.renderer.draw(e.x, e.y, e.char, color)
