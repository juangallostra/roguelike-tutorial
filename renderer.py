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

    def render_objects(self, elements):
        # render game state
        tcod.console_set_default_foreground(self._con, tcod.white)
        for e in elements:
            self.draw(e)

    def clear_objects(self, elements):
        for e in elements:
            self.clear(e)
    
    def render_map(self, game_map):
        for y in range(game_map.get_height()):
            for x in range(game_map.get_width()):
                wall = game_map.map[x][y].block_sight
                if wall:
                    tcod.console_set_char_background(self._con, x, y, game_map.color_dark_wall, tcod.BKGND_SET)
                else:
                    tcod.console_set_char_background(self._con, x, y, game_map.color_dark_ground, tcod.BKGND_SET)

    def render_all(self, objects, game_map):
        self.render_map(game_map)
        self.render_objects(objects)
        tcod.console_blit(self._con, 0, 0, self._width, self._height, 0, 0, 0)
        tcod.console_flush()
        self.clear_objects(objects)





