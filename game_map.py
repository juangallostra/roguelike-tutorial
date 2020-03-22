import libtcodpy as tcod

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
N_LEVELS = 3

class Tile():
    # A tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
 
        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
    
    def get_char(self):
        if self.blocked: return '#'
        return '.'

class Rect():
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.x2 = x + w
        self.y1 = y
        self.y2 =  y + h
    
    def center(self):
        # return room center
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)
 
    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class GameMap():
    def __init__(self, width, height):
        self._width = width
        self._height = height
        
        self._levels = N_LEVELS
        self.active_level = 0
        self.full_map = {i: [[Tile(True) for y in range(height)] for x in range(width)] for i in range(N_LEVELS)}
        self.map = self.full_map[self.active_level]
        
        self.color_dark_wall = tcod.Color(0, 0, 100)
        self.color_dark_ground = tcod.Color(50, 50, 150)
        self.color_stair = tcod.Color(124, 52, 37)

    def handle_keys(self, keypress=None):
        if keypress.vk == tcod.KEY_CHAR:
            if keypress.c == ord('z'):
                self.change_level(self.active_level + 1)
            if keypress.c == ord('x'):
                self.change_level(self.active_level - 1)


    def change_level(self, target_level):
        if 0 <= target_level < self._levels:
            self.active_level = target_level
            self.map = self.full_map[self.active_level]

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def create_room(self, rect):
        # create a room
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
        for level in range(self._levels):
            # Activate that level
            self.change_level(level)
            # Create a random dungeon
            rooms = []
            num_rooms = 0
 
            for r in range(MAX_ROOMS):
                # random width and height
                w = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
                h = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
                # random position without going out of the boundaries of the map
                x = tcod.random_get_int(0, 0, self._width - w - 1)
                y = tcod.random_get_int(0, 0, self._height - h - 1)
            
                new_room = Rect(x, y, w, h)
 
                # Run through the other rooms and see if they intersect with this one
                failed = False
                for other_room in rooms:
                    if new_room.intersect(other_room):
                        failed = True
                        break
                if not failed:
                # this means there are no intersections, so this room is valid
                # "paint" it to the map's tiles
                    self.create_room(new_room)
 
                    # center coordinates of new room, will be useful later
                    (new_x, new_y) = new_room.center()
    
                    if num_rooms == 0:
                        if level == 0:
                            # this is the first room on the first level, where the player starts at
                            self.player_initial_pos = (new_x, new_y)
                    else:
                        # all rooms after the first:
                        # connect it to the previous room with a tunnel
                        # center coordinates of previous room
                        (prev_x, prev_y) = rooms[num_rooms-1].center()
    
                        # draw a coin (random number that is either 0 or 1)
                        if tcod.random_get_int(0, 0, 1) == 1:
                            # first move horizontally, then vertically
                            self.create_tunnel(prev_x, new_x, prev_y, horizontal=True)
                            self.create_tunnel(prev_y, new_y, new_x, horizontal=False)
                        else:
                            # first move vertically, then horizontally
                            self.create_tunnel(prev_y, new_y, prev_x, horizontal=False)
                            self.create_tunnel(prev_x, new_x, new_y, horizontal=True)
 
                    # finally, append the new room to the list
                    rooms.append(new_room)
                    num_rooms += 1
        self.change_level(0)