class Collider:
    def __init__(self, solid=True):
        self.solid = solid

class CollisionSystem:
    def resolve(self, entities):
        return {
            (e.x, e.y): e
            for e in entities
            if e.collider and e.collider.solid
        }
