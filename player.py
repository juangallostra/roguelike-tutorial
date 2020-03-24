import libtcodpy as tcod

UP = 'up'
DOWN = 'down'

class BaseObject():
    def __init__(self, x, y, char, name, color = tcod.white, blocks=False):
        self.name = name
        self._char = char
        self._x = x
        self._y = y
        self._blocks = blocks
        self._color = color

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

    def move(self, dx, dy, game_map):
        if not game_map.map[self._x + dx][self._y + dy].blocked:
            self._x += dx
            self._y += dy
    
    def is_player(self):
        return False


class MainPlayer(BaseObject):
    def __init__(self, x, y, char):
        super().__init__(x, y, char)
    
    def is_player(self):
        return True

    def handle_keys(self, game_map, keypress=None):
        # movement keys
        if keypress.vk == tcod.KEY_UP:
            self.move(0, -1, game_map)
            game_map.fov_recompute = True
 
        elif keypress.vk == tcod.KEY_DOWN:
            self.move(0, 1, game_map)
            game_map.fov_recompute = True
 
        elif keypress.vk == tcod.KEY_LEFT:
            self.move(-1, 0, game_map)
            game_map.fov_recompute = True

        elif keypress.vk == tcod.KEY_RIGHT:
            self.move(1, 0, game_map)
            game_map.fov_recompute = True
        
        elif keypress.vk == tcod.KEY_CHAR:
            if keypress.c == ord('z') and game_map.map[self._x][self._y].stair[UP]:
                game_map.change_level(game_map.active_level + 1)
                game_map.fov_recompute = True
            if keypress.c == ord('x') and game_map.map[self._x][self._y].stair[DOWN]:
                game_map.change_level(game_map.active_level - 1)
                game_map.fov_recompute = True
