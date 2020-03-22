import libtcodpy as tcod

class Tile():
    # A tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
 
        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Rect():
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.x2 = x + w
        self.y1 = y
        self.y2 =  y + h

class GameMap():
    def __init__(self, width, height):
        self.map = [[Tile(True) for y in range(height)] for x in range(width)]
        self._width = width
        self._height = height
        self.color_dark_wall = tcod.Color(0, 0, 100)
        self.color_dark_ground = tcod.Color(50, 50, 150)

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def create_room(self, rect):
          for x in range(rect.x1 + 1, rect.x2):
                for y in range(rect.y1 + 1, rect.y2):
                    self.map[x][y].blocked = False
                    self.map[x][y].block_sight = False  

    def create_tunnel(self, c1, c2, fixed_coord, horizontal):
        # create a tunnel
        for c in range(min(c1, c2), max(c1, c2) + 1):
            x = c if horizontal else fixed_coord
            y = c if not horizontal else fixed_coord
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False

    def generate_map(self):
        #create two rooms
        room1 = Rect(20, 15, 10, 15)
        room2 = Rect(50, 15, 10, 15)
        self.create_room(room1)
        self.create_room(room2)
        # connect rooms
        self.create_tunnel(25, 55, 23, horizontal=True)
        self.create_tunnel(25, 55, 22, horizontal=True)