import libtcodpy as tcod

class Tile():
    # A tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
 
        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class GameMap():
    def __init__(self, width, height):
        self.map = [[Tile(False) for y in range(height)] for x in range(width)]
        self._width = width
        self._height = height
        self.color_dark_wall = tcod.Color(0, 0, 100)
        self.color_dark_ground = tcod.Color(50, 50, 150)

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def generate_map(self):
        self.map[30][22].blocked = True
        self.map[30][22].block_sight = True
        self.map[50][22].blocked = True
        self.map[50][22].block_sight = True
