import libtcodpy as tcod
from entities import *
from tile_loader import ORC_TILE, TROLL_TILE, HEALING_POTION_TILE, SWORD_TILE, SHIELD_TILE
from config import USE_TILES


ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
N_LEVELS = 3

UP = 'up'
DOWN = 'down'

MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2

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
    def __init__(self, width, height, logger=None):
        self.logger = logger

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
        # since there is no level data. This results in the 
        # FOV algorithm not working as expected
        self.fov_maps = None
        self.fov_map = None

        # item and monster chances, level configuration
        self._monster_chances = {ORC: 80, TROLL: 20}
        self._item_chances = {HEAL: 70, LIGHTNING: 10, FIREBALL: 10, CONFUSE: 10, SWORD:25}
        self._max_monsters = MAX_ROOM_MONSTERS
        self._max_items = MAX_ROOM_ITEMS

    def closest_monster(self, max_range, player):
        # find closest enemy, up to a maximum range, and in the player's FOV
        closest_enemy = None
        closest_dist = max_range + 1  # start with (slightly more than) maximum range
 
        for entity in self.level_objects:
            if entity.fighter and not entity == player and tcod.map_is_in_fov(
                self.fov_map, 
                entity.get_x_position(), 
                entity.get_y_position()
            ):
                # calculate distance between this object and the player
                dist = player.distance_to(entity)
                if dist < closest_dist:  # it's closer, so remember it
                    closest_enemy = entity
                    closest_dist = dist
        return closest_enemy

    def change_level(self, target_level, only_tile_map=False):
        # Change current dungeon level
        if 0 <= target_level < self._levels:
            self.active_level = target_level
            self.map = self.full_map[self.active_level]
            if not only_tile_map:
                self.fov_map = self.fov_maps[self.active_level]
                self.level_objects = self.map_objects[self.active_level]

    def is_blocked(self, x, y, to_check_against=None):
        to_check = self.level_objects
        if to_check_against is not None:
            to_check = to_check_against
        # first test the map tile
        if self.map[x][y].blocked:
            return True
        # now check for any blocking objects
        for element in to_check:
            if element.blocks and element.get_x_position() == x and element.get_y_position() == y:
                return True
        return False

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def random_choice_index(self, chances):  
        # choose one option from list of chances, returning its index
        # the dice will land on some number between 1 and the sum of the chances
        dice = tcod.random_get_int(0, 1, sum(chances))
 
        # go through all chances, keeping the sum so far
        running_sum = 0
        choice = 0
        for w in chances:
            running_sum += w
            # see if the dice landed in the part that corresponds to this choice
            if dice <= running_sum:
                return choice
            choice += 1

    def random_choice(self, chances_dict):
        # choose one option from dictionary of chances, returning its key
        chances = chances_dict.values()
        keys = list(chances_dict.keys())
        return keys[self.random_choice_index(chances)]

    def from_dungeon_level(self, table, level):
        # returns a value that depends on level. 
        # the table specifies what value occurs after each level, default is 0.
        for (value, d_level) in reversed(table):
            if level >= d_level:
                return value
        return 0

    def update_item_chances(self, level): 
        # maximum number of items per room
        # Table is: [num_items, level]
        self._max_items = self.from_dungeon_level([[1, 0], [1, 1], [2, 2]], level)
 
        # chance of each item (by default they have a chance of 0 at level 1, which then goes up)
        self._item_chances = {}
        self._item_chances[HEAL] = 35  # healing potion always shows up, even if all other items have 0 chance
        self._item_chances[SWORD] = 10
        self._item_chances[SHIELD] = 10
        self._item_chances[LIGHTNING] = self.from_dungeon_level([[25, 4]], level)
        self._item_chances[FIREBALL] =  self.from_dungeon_level([[25, 6]], level)
        self._item_chances[CONFUSE] =   self.from_dungeon_level([[10, 2]], level)

    def update_monster_chances(self, level):
        # update chances to level
        # maximum number of monsters per room
        # Table is: [num_monsters, level]
        self._max_monsters = self.from_dungeon_level([[1, 0],[2, 1], [3, 4], [5, 6]], level)
 
        # chance of each monster
        self._monster_chances = {}
        self._monster_chances[ORC] = 80  # orc always shows up, even if all other monsters have 0 chance
        self._monster_chances[TROLL] = self.from_dungeon_level([[15, 3], [30, 5], [60, 7]], level)


    def place_objects_in_room(self, level, room):
        # place objects
        # choose random number of items
        num_items = tcod.random_get_int(0, 0, self._max_items)
 
        for i in range(num_items):
            # choose random spot for this item
            x = tcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
            y = tcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
 
            # only place it if the tile is not blocked
            if not self.is_blocked(x, y, self.map_objects[level]):
                choice = self.random_choice(self._item_chances)
                if choice == HEAL:
                    # create a healing potion (70% chance)
                    item_component = Item(use_function=cast_heal)
                    item = BaseObject(
                        x, 
                        y, 
                        HEALING_POTION_TILE[USE_TILES].code, 
                        'Healing Potion', 
                        HEALING_POTION_TILE[USE_TILES].color, 
                        logger=self.logger,
                        item=item_component,
                        always_visible=True
                    )
                elif choice == LIGHTNING:
                    # create a lightning bolt scroll (10% chance)
                    item_component = Item(use_function=cast_lighting)
                    item = BaseObject(
                        x,
                        y,
                        '#',
                        'scroll of lightning bolt',
                        tcod.light_yellow,
                        logger=self.logger,
                        item=item_component,
                        always_visible=True
                    )
                elif choice == FIREBALL:
                    # create a fireball scroll (10% chance)
                    item_component = Item(use_function=cast_fireball)
                    item = BaseObject(
                        x, 
                        y, 
                        '#', 
                        'scroll of fireball', 
                        tcod.dark_flame,
                        logger=self.logger,
                        item=item_component,
                        always_visible=True)
                elif choice == CONFUSE:
                    # create a confuse scroll (15% chance)
                    item_component = Item(use_function=cast_confuse)
                    item = BaseObject(
                        x, 
                        y, 
                        '#', 
                        'scroll of confusion', 
                        tcod.light_blue,
                        logger=self.logger,
                        item=item_component,
                        always_visible=True
                    )
                elif choice == SWORD:
                    # create a sword
                    equipment_component = Equipment(slot=RIGHT_HAND, power_bonus=3)
                    item = BaseObject(
                        x, 
                        y, 
                        SWORD_TILE[USE_TILES].code, 
                        'sword', 
                        SWORD_TILE[USE_TILES].color,
                        logger=self.logger,
                        equipment=equipment_component,
                        always_visible=True)            
                elif choice == SHIELD:
                    # create a shield
                    equipment_component = Equipment(slot=LEFT_HAND, defense_bonus=1)
                    item = BaseObject(
                        x,
                        y,
                        SHIELD_TILE[USE_TILES].code,
                        'shield',
                        SHIELD_TILE[USE_TILES].color,
                        logger=self.logger,
                        equipment=equipment_component,
                        always_visible=True
                    )

                self.map_objects[level].append(item)
                # item.send_to_back()  #items appear below other objects

        # choose random number of monsters
        num_monsters = tcod.random_get_int(0, 0, self._max_monsters)
 
        for i in range(num_monsters):
            # choose random spot for this monster
            x = tcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
            y = tcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
            if not self.is_blocked(x, y, self.map_objects[level]):
                choice = self.random_choice(self._monster_chances)
                if choice == ORC:
                    # 80% chance of getting an orc
                    # create an orc
                    fighter_component = Fighter(hp=10, defense=0, power=3, xp=35, death_function=monster_death)
                    ai_component = BasicMonster()
                    monster = BaseObject(
                        x,
                        y,
                        ORC_TILE[USE_TILES].code,
                        ORC,
                        ORC_TILE[USE_TILES].color,
                        blocks=True,
                        fighter=fighter_component,
                        ai=ai_component,
                        logger=self.logger)
                elif choice == TROLL:
                    # create a troll
                    fighter_component = Fighter(hp=16, defense=1, power=4, xp=100, death_function=monster_death)
                    ai_component = BasicMonster()
                    monster = BaseObject(
                        x,
                        y,
                        TROLL_TILE[USE_TILES].code,
                        TROLL,
                        TROLL_TILE[USE_TILES].color,
                        blocks=True,
                        fighter=fighter_component,
                        ai=ai_component,
                        logger=self.logger)
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
            self.update_item_chances(level)
            self.update_monster_chances(level)
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
        # Now that we know which tiles are blocked, generate FOV maps
        # for each level
        self.init_fov()
        self.change_level(0)
    
    def init_fov(self):
        # Generate Field of View maps
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
