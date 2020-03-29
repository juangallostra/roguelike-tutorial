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
        logger=None,
        item=None,
        always_visible=False
    ):
        self.name = name
        self._char = char
        self._x = x
        self._y = y
        self.blocks = blocks
        self.always_visible = always_visible
        self._color = color
        # Add components
        self.fighter = fighter
        if self.fighter: # let the fighter component know who owns it 
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  # let the AI component know who owns it
            self.ai.owner = self

        self.item = item # let the item component know who owns it
        if self.item:
            self.item.owner = self

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

    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self._x) ** 2 + (y - self._y) ** 2)

    def move(self, dx, dy, game_map):
        if not game_map.is_blocked(self._x + dx, self._y + dy):
            self._x += dx
            self._y += dy

    def is_player(self):
        return False


## Components
class Fighter():
    # Combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, xp=0, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.xp = xp
        self.defense = defense
        self.power = power
        self.death_function = death_function
        self.owner = None
    
    def take_damage(self, damage, player):
        # apply damage if possible
        if damage > 0:
            self.hp -= damage
        # check for death. if there's a death function, call it
        if self.hp <= 0:
            if self.death_function is not None:
                self.death_function(self.owner)
            self.hp = 0
            if self.owner != player:  # yield experience to the player
                player.fighter.xp += self.xp
    
    def attack(self, target, player=None):
        # if there is no player, assume the target is the player
        if player is None and target.is_player():
            player = target
        # a simple formula for attack damage
        damage = self.power - target.fighter.defense
 
        if damage > 0:
            # if owner has a logger log message
            self.owner.logger.log_message(
                self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.'
            )
            # make the target take some damage
            target.fighter.take_damage(damage, player)
        else:
            self.owner.logger.log_message(
                self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!'
            )
    def heal(self, amount):
        # heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp


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


class ConfusedMonster():
    # AI for a temporarily confused monster (reverts to previous AI after a while).
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.owner = None
        self.old_ai = old_ai
        self.num_turns = num_turns
 
    def take_turn(self, game_map=None, player=None):
        if self.num_turns > 0:  # still confused...
            # move in a random direction, and decrease the number of turns confused
            self.owner.move(tcod.random_get_int(0, -1, 1), tcod.random_get_int(0, -1, 1), game_map)
            self.num_turns -= 1
 
        else:  
            # restore the previous AI 
            # (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            self.owner.logger.log_message('The ' + self.owner.name + ' is no longer confused!', tcod.red)


class Item():
    def __init__(self, use_function=None):
        self.use_function = use_function
        self.owner = None # The object (ex. potion) has this item component

    # an item that can be picked up and used.
    def pick_up(self, inventory, game_map):
        # add to the player's inventory and remove from the map
        if len(inventory) >= MAX_ITEMS:
            self.owner.logger.log_message('Your inventory is full, cannot pick up ' + self.owner.name + '.', tcod.red)
        else:
            # Add object to inventory and remove from map
            inventory.append(self.owner)
            game_map.level_objects.remove(self.owner)
            game_map.map_objects[game_map.active_level].remove(self.owner)
            self.owner.logger.log_message('You picked up a ' + self.owner.name + '!', tcod.green)

    def drop(self, inventory, game_map, player):
        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        game_map.level_objects.append(self.owner)
        game_map.map_objects[game_map.active_level].append(self.owner)
        inventory.remove(self.owner)
        self.owner._x = player.get_x_position()
        self.owner._y = player.get_y_position()
        player.logger.log_message('You dropped a ' + self.owner.name + '.', tcod.yellow)

    def use(self, inventory, **kwargs):
        # Params that can be passed to use:
        # player = kwargs['player']
        # game_map = kwargs['game_map']
        # renderer = kwargs['renderer']
        # names_under_mouse = kwargs['names_under_mouse']
        # show_map_chars = kwargs['show_map_chars']
        # mouse = kwargs['mouse']
        # key = kwargs['key']
        # just call the "use_function" if it is defined
        if self.use_function is None:
            self.owner.logger.log_message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function(**kwargs) != 'cancelled':
                inventory.remove(self.owner)  # destroy after use, unless it was cancelled for some reason


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

    def clear_messages(self):
        self.game_msgs = []

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
        self.state = PLAYING # initial game state
        # inventory
        self.inventory = []
        self.level = 1
    
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
                if keypress.c == ord('g'):
                    # pick up an item
                    for o in game_map.level_objects:  # look for an item in the player's tile
                        if o.get_x_position() == self._x and o.get_y_position() == self._y and o.item:
                            o.item.pick_up(self.inventory, game_map)
                            break
                if keypress.c == ord('i'):
                    # show the inventory
                    return SHOW_INVENTORY
                if keypress.c == ord('d'):
                    # show the inventory; if an item is selected, drop it
                    return DROP_ITEM
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
            self.fighter.attack(target, self)
        else:
            self.move(dx, dy, game_map)
            game_map.fov_recompute = True
    
    def check_level_up(self):
        # see if the player's experience is enough to level-up
        level_up_xp = LEVEL_UP_BASE + self.level * LEVEL_UP_FACTOR
        if self.fighter.xp >= level_up_xp:
            # it is! level up
            self.level += 1
            self.fighter.xp -= level_up_xp
            self.logger.log_message('Your battle skills grow stronger! You reached level ' + str(self.level) + '!', tcod.yellow)
            return True
        return False


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

# item functions. They receive the player and the game_map as params
def cast_heal(**kwargs):        
    # heal the player
    player = kwargs['player']
    if player.fighter.hp == player.fighter.max_hp:
        player.logger.log_message('You are already at full health.', tcod.red)
        return 'cancelled'
 
    player.logger.log_message('Your wounds start to feel better!', tcod.light_violet)
    player.fighter.heal(HEAL_AMOUNT)

def cast_lighting(**kwargs):
    #find closest enemy (inside a maximum range) and damage it
    player = kwargs['player']
    game_map = kwargs['game_map']
    monster = game_map.closest_monster(LIGHTNING_RANGE, player)
    if monster is None:  #no enemy found within maximum range
        player.logger.log_message('No enemy is close enough to strike.', tcod.red)
        return 'cancelled'
 
    #zap it!
    player.logger.log_message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
        + str(LIGHTNING_DAMAGE) + ' hit points.', tcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE, player)

def cast_confuse(**kwargs):
    # find closest enemy in-range and confuse it
    player = kwargs['player']
    game_map = kwargs['game_map']
    # ask the player for a target to confuse
    player.logger.log_message('Left-click an enemy to confuse it, or right-click to cancel.', tcod.light_cyan)
    monster = target_monster(max_range=CONFUSE_RANGE,**kwargs)
    if monster is None: return 'cancelled'
    # replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  # tell the new component who owns it
    player.logger.log_message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', tcod.light_green)

def cast_fireball(**kwargs):
    # find closest enemy in-range and confuse it
    player = kwargs['player']
    game_map = kwargs['game_map']
    renderer = kwargs['renderer']
    names_under_mouse = kwargs['names_under_mouse']
    show_map_chars = kwargs['show_map_chars']
    mouse = kwargs['mouse']
    key = kwargs['key']
    # ask the player for a target tile to throw a fireball at
    player.logger.log_message('Left-click a target tile for the fireball, or right-click to cancel.', tcod.light_cyan)
    (x, y) = target_tile(
        max_range=None, 
        mouse=mouse,
        key=key,
        renderer=renderer,
        game_map=game_map,
        player=player,
        names_under_mouse=names_under_mouse,
        show_map_chars=show_map_chars
    )
    if x is None: return 'cancelled'
    player.logger.log_message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', tcod.orange)
 
    for obj in game_map.level_objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            player.logger.log_message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', tcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE, player)

## Helper methods
def target_tile(
        max_range=None, 
        mouse=None, 
        key=None, 
        renderer=None, 
        game_map=None,
        player=None,
        names_under_mouse=None,
        show_map_chars=False
    ):
    # return the position of a tile left-clicked in player's 
    # FOV (optionally in a range), or (None,None) if right-clicked.
    while True:
        # render the screen. this erases the inventory and
        # shows the names of objects under the mouse.
        tcod.console_flush()
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)
        objects = game_map.level_objects + [player]
        renderer.render_all(objects, game_map, names_under_mouse, show_map_chars)
 
        (x, y) = (mouse.cx, mouse.cy)
 
        # accept the target if the player clicked in FOV, and in case 
        # a range is specified, if it's in that range
        if (mouse.lbutton_pressed and tcod.map_is_in_fov(game_map.fov_map, x, y) and
            (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)
        if mouse.rbutton_pressed or key.vk == tcod.KEY_ESCAPE:
            return (None, None)  # cancel if the player right-clicked or pressed Escape

def target_monster(**kwargs):
    # returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(**kwargs)
        if x is None:  #player cancelled
            return None
 
        # return the first clicked monster, otherwise continue looping
        for obj in kwargs['game_map'].level_objects:
            if obj.get_x_position() == x and obj.get_y_position() == y and obj.fighter and obj != kwargs['player']:
                return obj
