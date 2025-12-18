from colorama import Back

class Entity:
    def __init__(self, x, y, char="█", color=Back.WHITE):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.char = char
        self.color = color
        self.collider = None
        self.light = None

    def move_to(self, new_x, new_y):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x = new_x
        self.y = new_y