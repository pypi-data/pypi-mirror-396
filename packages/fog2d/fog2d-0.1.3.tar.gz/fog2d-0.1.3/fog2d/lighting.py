import math

class Light:
    def __init__(self, radius=5, intensity=1.0):
        self.radius = radius
        self.intensity = intensity

class LightSystem:
    def light_at(self, x, y, lights):
        value = 0
        for l, lx, ly in lights:
            d = math.dist((x, y), (lx, ly))
            if d < l.radius:
                value += (1 - d / l.radius) * l.intensity
        return min(value, 1.0)
