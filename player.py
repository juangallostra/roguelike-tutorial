import libtcodpy as tcod

class BaseObject():
    def __init__(self, x, y, char):
        self._char = char
        self._x = x
        self._y = y
        self._color = tcod.white

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

    def move(self, dx, dy):
        self._x += dx
        self._y += dy


class MainPlayer(BaseObject):
    def __init__(self, x, y, char):
        super().__init__(x, y, char)
    
    def handle_keys(self, keypress=None):
        # movement keys
        if keypress.vk == tcod.KEY_UP:
            self.move(0, -1)
 
        elif keypress.vk == tcod.KEY_DOWN:
            self.move(0, 1)
 
        elif keypress.vk == tcod.KEY_LEFT:
            self.move(-1, 0)

        elif keypress.vk == tcod.KEY_RIGHT:
            self.move(1, 0)

