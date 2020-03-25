import libtcodpy as tcod
from constants import PLAYING, DIDNT_TAKE_TURN
import math

UP = 'up'
DOWN = 'down'


class BaseObject():
    def __init__(self, x, y, char, name, color=tcod.white, blocks=False, fighter=None, ai=None):
        self.name = name
        self._char = char
        self._x = x
        self._y = y
        self.blocks = blocks
        self._color = color
        # Add components
        self.fighter = fighter
        if self.fighter: # let the fighter component know who owns it 
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  # let the AI component know who owns it
            self.ai.owner = self

    def get_color(self):
        return self._color

    def get_char(self):
        return self._char

    def get_position(self):
        return self._x, self._y

    def get_x_position(self):
        return self._x

    def get_y_position(self):
        return self._y
    
    def distance_to(self, other):
        # return the distance to another object
        dx = other.get_x_position() - self._x
        dy = other.get_y_position() - self._y
        return math.sqrt(dx ** 2 + dy ** 2)

    def move(self, dx, dy, game_map):
        if not game_map.is_blocked(self._x + dx, self._y + dy):
            self._x += dx
            self._y += dy

    def is_player(self):
        return False


class Fighter():
    # Combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
    
    def take_damage(self, damage):
        # apply damage if possible
        if damage > 0:
            self.hp -= damage
    
    def attack(self, target):
        # a simple formula for attack damage
        damage = self.power - target.fighter.defense
 
        if damage > 0:
            # make the target take some damage
            print(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            print(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')


class BasicMonster():
    # AI for a basic monster.
    def move_towards(self, target_x, target_y, game_map):
        # vector from this object to the target, and distance
        dx = target_x - self.owner.get_x_position()
        dy = target_y - self.owner.get_y_position()
        distance = math.sqrt(dx ** 2 + dy ** 2)
 
        # normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(dx // distance)
        dy = int(dy // distance)
        self.owner.move(dx, dy, game_map)

    def take_turn(self, game_map, player):
        # a basic monster takes its turn. If you can see it, it can see you
        monster = self.owner
        if tcod.map_is_in_fov(game_map.fov_map, monster.get_x_position(), monster.get_y_position()):
            # move towards player if far away
            if monster.distance_to(player) >= 2:
                self.move_towards(player.get_x_position(), player.get_y_position(), game_map)
 
            # close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)


class MainPlayer(BaseObject):
    def __init__(self, x, y, char, name, color=tcod.white, blocks=True, fighter=None, ai=None):
        super().__init__(x, y, char, name, color, blocks, fighter, ai)
    
    def is_player(self):
        return True

    def handle_keys(self, game_map, game_state, keypress=None):
        # Only handle game key presses if playing
        if game_state == PLAYING:
            # movement keys
            if keypress.vk == tcod.KEY_UP:
                self.move_or_attack(0, -1, game_map)
                game_map.fov_recompute = True
                return 
            elif keypress.vk == tcod.KEY_DOWN:
                self.move_or_attack(0, 1, game_map)
                game_map.fov_recompute = True
                return
            elif keypress.vk == tcod.KEY_LEFT:
                self.move_or_attack(-1, 0, game_map)
                game_map.fov_recompute = True
                return
            elif keypress.vk == tcod.KEY_RIGHT:
                self.move_or_attack(1, 0, game_map)
                game_map.fov_recompute = True
                return
            elif keypress.vk == tcod.KEY_CHAR:
                if keypress.c == ord('z') and game_map.map[self._x][self._y].stair[UP]:
                    game_map.change_level(game_map.active_level + 1)
                    game_map.fov_recompute = True
                    return
                if keypress.c == ord('x') and game_map.map[self._x][self._y].stair[DOWN]:
                    game_map.change_level(game_map.active_level - 1)
                    game_map.fov_recompute = True
                    return
        return DIDNT_TAKE_TURN

    def move_or_attack(self, dx, dy, game_map):
        #the coordinates the player is moving to/attacking
        x = self.get_x_position() + dx
        y = self.get_y_position() + dy
 
        #try to find an attackable object there
        target = None
        for o in game_map.level_objects:
            if o.get_x_position() == x and o.get_y_position() == y:
                target = o
                break
 
        #attack if target found, move otherwise
        if target is not None:
            self.fighter.attack(target)
        else:
            self.move(dx, dy, game_map)
            game_map.fov_recompute = True
