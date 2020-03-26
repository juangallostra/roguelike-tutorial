import libtcodpy as tcod
from constants import *
import math
import textwrap

UP = 'up'
DOWN = 'down'

## Base entity
class BaseObject():
    def __init__(
        self, 
        x, 
        y, 
        char, 
        name, 
        color=tcod.white, 
        blocks=False, 
        fighter=None, 
        ai=None, 
        logger=None
    ):
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

        self.logger = logger

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color 

    def get_char(self):
        return self._char
    
    def set_char(self, new_char):
        self._char = new_char

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

## Components
class Fighter():
    # Combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function
        self.owner = None
    
    def take_damage(self, damage):
        # apply damage if possible
        if damage > 0:
            self.hp -= damage
        # check for death. if there's a death function, call it
        if self.hp <= 0:
            if self.death_function is not None:
                self.death_function(self.owner)
            self.hp = 0
    
    def attack(self, target):
        # a simple formula for attack damage
        damage = self.power - target.fighter.defense
 
        if damage > 0:
            # if owner has a logger log message
            self.owner.logger.log_message(
                self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.'
            )
            # make the target take some damage
            target.fighter.take_damage(damage)
        else:
            self.owner.logger.log_message(
                self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!'
            )


class BasicMonster():
    def __init__(self):
        self.owner = None
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

class Logger():
    def __init__(self):
        # message log
        # create the list of game messages and their colors, starts empty
        self.game_msgs = []

    def log_message(self, new_msg, color=tcod.white):
        # split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
 
        for line in new_msg_lines:
            # if the buffer is full, remove the first line to make room for the new one
            if len(self.game_msgs) == MSG_HEIGHT:
                del self.game_msgs[0]
 
            # add the new line as a tuple, with the text and the color
            self.game_msgs.append( (line, color) )


## Main player
class MainPlayer(BaseObject):
    def __init__(
        self,
        x, 
        y, 
        char, 
        name, 
        color=tcod.white, 
        blocks=True, 
        fighter=None, 
        ai=None,
        logger=None
    ):
        super().__init__(x, y, char, name, color, blocks, fighter, ai, logger)
        self.state = PLAYING
    
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
        # the coordinates the player is moving to/attacking
        x = self.get_x_position() + dx
        y = self.get_y_position() + dy
 
        # try to find an attackable object there
        target = None
        for o in game_map.level_objects:
            if o.fighter and o.get_x_position() == x and o.get_y_position() == y:
                target = o
                break
 
        # attack if target found, move otherwise
        if target is not None:
            self.fighter.attack(target)
        else:
            self.move(dx, dy, game_map)
            game_map.fov_recompute = True

# death functions
def player_death(player):
    # the game ended!
    if player.logger:
        player.logger.log_message('You died!')
    player.state = DEAD
 
    # for added effect, transform the player into a corpse!
    player.set_char('%')
    player.set_color(tcod.dark_red)
 
def monster_death(monster):
    # transform it into a nasty corpse! it doesn't block, can't be
    # attacked and doesn't move
    if monster.logger:
        monster.logger.log_message(monster.name.capitalize() + ' is dead!')

    monster.set_char('%')
    monster.set_color(tcod.dark_red)
    
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name