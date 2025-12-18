from colorama import Back

class Entity:
    def __init__(self, x, y, char="█", color=Back.WHITE):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.collider = None
        self.light = None
