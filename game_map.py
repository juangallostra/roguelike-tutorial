import libtcodpy as tcod
from entities import BaseObject

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
N_LEVELS = 3

UP = 'up'
DOWN = 'down'

MAX_ROOM_MONSTERS = 3

class Tile():
    # A tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        # is it a wall?
        self.blocked = blocked
        # is it a stair?
        self.stair = {'up': False, 'down': False}      
        # has it been explored?
        self.explored = False
        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
    
    def get_char(self):
        # Get character representing the object
        if self.blocked: return '#'
        if self.stair[UP]: return '>'
        if self.stair[DOWN]: return '<'
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
        self.full_map = {
            i: [[Tile(True) for y in range(height)] for x in range(width)] for i in range(N_LEVELS)
        }

        # Create an empty list of objects per level
        self.level_objects = None
        self.map_objects = [[] for i in range(self._levels)]

        # Forces FOV recalculation
        self.fov_recompute = True # light the initial position of the player
        # FOV maps have to be generated after dungeon generation
        # because if they are created before all tiles are blocked
        # the FOV algorithm doesn't work as expected
        self.fov_maps = None
        self.fov_map = None 

    def change_level(self, target_level, only_tile_map=False):
        # Change current dungeon level
        if 0 <= target_level < self._levels:
            self.active_level = target_level
            self.map = self.full_map[self.active_level]
            if not only_tile_map:
                self.fov_map = self.fov_maps[self.active_level]
                self.level_objects = self.map_objects[self.active_level]

    def is_blocked(self, x, y):
        # first test the map tile
        if self.map[x][y].blocked:
            return True
        #now check for any blocking objects
        for element in self.level_objects:
            if element.blocks and element.get_x_position() == x and element.get_y_position() == y:
                return True
        return False

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def place_objects_in_room(self, level, room):
        # choose random number of monsters
        num_monsters = tcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)
 
        for i in range(num_monsters):
            #choose random spot for this monster
            x = tcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
            y = tcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
 
            if tcod.random_get_int(0, 0, 100) < 80:  #80% chance of getting an orc
                #create an orc
                monster = BaseObject(x, y, 'O', tcod.desaturated_green)
            else:
                #create a troll
                monster = BaseObject(x, y, 'T', tcod.darker_green)
            # Append it to the list ob level objects
            self.map_objects[level].append(monster)

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

    def add_stairs(self):
        # connect all levels with stairs
        # for each level, find a tile that connects with
        # the next level
        for level in range(self._levels - 1):
            valid_stair = False
            while not valid_stair:
                # pick a random tile
                x = tcod.random_get_int(0, 0, self._width - 1)
                y = tcod.random_get_int(0, 0, self._height - 1)
                # Check if it is walkable in levels being connected
                if not self.full_map[level][x][y].blocked and not self.full_map[level + 1][x][y].blocked:
                    self.full_map[level][x][y].stair[UP] = True
                    self.full_map[level + 1][x][y].stair[DOWN] = True
                    valid_stair = True

    def generate_map(self):
        # Generate the dungeon map
        # 1. Rooms
        # 2. Tunnels
        # 3. Stairs
        # 4. FOV map (so that we can know which tiles let the light pass through)
        for level in range(self._levels):
            # Activate that level
            self.change_level(level, only_tile_map=True)
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
 
                    # generate room monsters
                    self.place_objects_in_room(level, new_room)
                    # finally, append the new room to the list
                    rooms.append(new_room)
                    num_rooms += 1

        self.add_stairs()

        self.fov_maps = {
            i: tcod.map_new(self._width, self._height) for i in range(N_LEVELS)
        }
        for level in range(self._levels):
            for y in range(self._height):
                for x in range(self._width):
                    tcod.map_set_properties(
                        self.fov_maps[level],
                        x,
                        y,
                        not self.full_map[level][x][y].block_sight,
                        not self.full_map[level][x][y].blocked
                    )

        self.change_level(0)