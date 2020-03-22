import libtcodpy as tcod

class RenderScreen():
    def __init__(self, width, height):
        # Auxiliary console
        self._con = tcod.console_new(width, height)
        self._width = width
        self._height = height

    def draw(self, element):
        # set the color and then draw the character that represents this object at its position
        tcod.console_set_default_foreground(self._con, element.get_color())
        tcod.console_put_char(self._con, element.get_x_position(), element.get_y_position(), element.get_char(), tcod.BKGND_NONE)

    def clear(self, element):
        # erase the character that represents this object
        tcod.console_put_char(self._con, element.get_x_position(), element.get_y_position(), ' ', tcod.BKGND_NONE)

    def render(self, elements):
        tcod.console_set_default_foreground(self._con, tcod.white)
        for e in elements:
            self.draw(e)
            tcod.console_blit(self._con, 0, 0, self._width, self._height, 0, 0, 0)
            tcod.console_flush()
            self.clear(e)

