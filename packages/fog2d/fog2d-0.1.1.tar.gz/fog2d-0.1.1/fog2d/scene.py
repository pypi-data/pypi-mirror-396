from colorama import Back
from .collision import CollisionSystem
from .lighting import LightSystem

class Scene:
    def __init__(self, renderer):
        self.renderer = renderer
        self.entities = []
        self.collision = CollisionSystem()
        self.light_system = LightSystem()

    def add(self, entity):
        self.entities.append(entity)

    def update(self):
        self.collision.resolve(self.entities)

    def render(self):
        lights = [(e.light, e.x, e.y) for e in self.entities if e.light]
        for e in self.entities:
            brightness = self.light_system.light_at(e.x, e.y, lights)
            color = e.color
            if brightness < 0.2:
                color = Back.BLACK
            elif brightness < 0.5:
                color = Back.BLUE
            self.renderer.draw(e.x, e.y, e.char, color)
