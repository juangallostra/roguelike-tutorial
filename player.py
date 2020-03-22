import libtcodpy as tcod

class BasePlayer():
    def __init__(self, x, y, char):
        self._char = char
        self._x = x
        self._y = y

    def get_char(self):
        return self._char

    def get_position(self):
        return self._x, self._y

    def get_x_position(self):
        return self._x

    def get_y_position(self):
        return self._y


class MainPlayer(BasePlayer):
    def __init__(self, x, y, char):
        super().__init__(x, y, char)
    
    def handle_keys(self, keypress=None):
        # movement keys
        if keypress.vk == tcod.KEY_UP:
            self._y = self._y - 1
 
        elif keypress.vk == tcod.KEY_DOWN:
            self._y = self._y + 1
 
        elif keypress.vk == tcod.KEY_LEFT:
            self._x = self._x - 1
 
        elif keypress.vk == tcod.KEY_RIGHT:
            self._x = self._x + 1
