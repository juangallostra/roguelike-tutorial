import libtcodpy as tcod

class RenderScreen():
    def __init__(self):
        pass

    def render(self, elements):
        # print(self.get_prev_position(), self.get_position())
        for e in elements:
            tcod.console_put_char(
                0, 
            e.get_x_position(),
            e.get_y_position(),
            e.get_char(),
            tcod.BKGND_NONE
        )
        tcod.console_flush()
        tcod.console_put_char(0, e.get_x_position(), e.get_y_position(), ' ', tcod.BKGND_NONE)

