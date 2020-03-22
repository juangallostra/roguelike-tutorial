import libtcodpy as tcod

class RenderScreen():
    def __init__(self, width, height):
        # Auxiliary console
        self._con = tcod.console_new(width, height)
        self._width = width
        self._height = height


    def render(self, elements):
        tcod.console_set_default_foreground(self._con, tcod.white)
        for e in elements:
            tcod.console_put_char(
            self._con, 
            e.get_x_position(),
            e.get_y_position(),
            e.get_char(),
            tcod.BKGND_NONE
        )
        tcod.console_blit(self._con, 0, 0, self._width, self._height, 0, 0, 0)
        tcod.console_flush()
        tcod.console_put_char(self._con, e.get_x_position(), e.get_y_position(), ' ', tcod.BKGND_NONE)

