import libtcodpy as tcod
import textwrap
from constants import *

# Colors
C_DARK_WALL = tcod.Color(0, 0, 100)
C_LIGHT_WALL = tcod.Color(130, 110, 50)
C_DARK_GROUND = tcod.Color(50, 50, 150)
C_LIGHT_GROUND = tcod.Color(200, 180, 50)
C_STAIR = tcod.Color(124, 52, 37)
C_LIGHT_STAIR = tcod.Color(186, 142, 32)
C_BLACK = tcod.Color(0, 0, 0)

UP = 'up'
DOWN = 'down'

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 5

class RenderScreen():
    def __init__(self, width, height, panel_height, logger):
        # Auxiliary console
        self._con = tcod.console_new(width, height)
        # GUI panel
        self._panel = tcod.console_new(width, panel_height)
        # Menu (don't create it yet, it has variable size)
        self._window = None
        self._width = width
        self._height = height
        self._panel_height = panel_height
        self.logger = logger

    def menu(self, header, options, width):
        if len(options) > MAX_MENU_OPTIONS: 
            raise ValueError('Cannot have a menu with more than'+ str(MAX_MENU_OPTIONS) +'options.')
        # calculate total height for the header (after auto-wrap) and one line per option
        header_height = tcod.console_get_height_rect(self._con, 0, 0, width, self._height, header)
        height = len(options) + header_height
        #create an off-screen console that represents the menu's window
        self._window = tcod.console_new(width, height)
 
        #print the header, with auto-wrap
        tcod.console_set_default_foreground(self._window, tcod.white)
        tcod.console_print_rect_ex(
            self._window, 
            0, 
            0, 
            width, 
            height, 
            tcod.BKGND_NONE, 
            tcod.LEFT, 
            header
        )
        # print all the options
        y = header_height
        letter_index = ord('a')
        for option_text in options:
            text = '(' + chr(letter_index) + ') ' + option_text
            tcod.console_print_ex(self._window, 0, y, tcod.BKGND_NONE, tcod.LEFT, text)
            y += 1
            letter_index += 1
        # blit the contents of "window" to the root console
        x = int(self._width/2 - width/2)
        y = int(self._height/2 - height/2)
        tcod.console_blit(self._window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
        # present the root console to the player and wait for a key-press
        tcod.console_flush()
        key = tcod.console_wait_for_keypress(True)

    def draw(self, element, game_map):
        # only draw objects that are in the Field of View
        if tcod.map_is_in_fov(
            game_map.fov_map,
            element.get_x_position(),
            element.get_y_position()
        ):
            # set the color and then draw the character that represents this object at its position
            tcod.console_set_default_foreground(self._con, element.get_color())
            tcod.console_put_char(
                self._con,
                element.get_x_position(),
                element.get_y_position(),
                element.get_char(),
                tcod.BKGND_NONE
            )

    def clear(self, element):
        # erase the character that represents this object
        tcod.console_put_char(
            self._con,
            element.get_x_position(),
            element.get_y_position(),
            ' ',
            tcod.BKGND_NONE
        )

    def render_bar(self, x, y, total_width, name, value, maximum, bar_color,  back_color):
        # render a bar (HP, experience, etc). 
        # first calculate the width of the bar
        bar_width = int(float(value) / maximum * total_width)
 
        # render the background first
        tcod.console_set_default_background(self._panel, back_color)
        tcod.console_rect(self._panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)
 
        # now render the bar on top
        tcod.console_set_default_background(self._panel, bar_color)
        if bar_width > 0:
            tcod.console_rect(self._panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)
        # finally, some centered text with the values
        tcod.console_set_default_foreground(self._panel, tcod.white)
        tcod.console_print_ex(self._panel, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER,
            name + ': ' + str(value) + '/' + str(maximum))

    def render_inventory_menu(self, header, inventory):
        # show a menu with each item of the inventory as an option
        if len(inventory) == 0:
            options = ['Inventory is empty.']
        else:
            options = [item.name for item in inventory]
 
        index = self.menu(header, options, INVENTORY_WIDTH)

    def render_objects(self, elements, game_map):
        # render game state
        tcod.console_set_default_foreground(self._con, tcod.white)
        for e in elements:
            self.draw(e, game_map)

    def clear_objects(self, elements):
        for e in elements:
            self.clear(e)
    
    def render_map(self, game_map, player, show_chars=False):
        tcod.console_set_default_foreground(self._con, tcod.white)
        
        if game_map.fov_recompute:
            # recompute FOV if needed (the player moved or something)
            game_map.fov_recompute = False
            game_map.fov_map.compute_fov(
                player.get_x_position(),
                player.get_y_position(),
                TORCH_RADIUS,
                FOV_LIGHT_WALLS,
                FOV_ALGO
            )
        
        for y in range(game_map.get_height()):
            for x in range(game_map.get_width()):
                visible = tcod.map_is_in_fov(game_map.fov_map, x, y)
                wall = game_map.map[x][y].block_sight
                if show_chars:
                    tcod.console_put_char(
                        self._con,
                        x,
                        y,
                        game_map.map[x][y].get_char(),
                        tcod.BKGND_NONE
                    )
                if not visible:
                    # Set tile to black if it is not visible
                    tcod.console_set_char_background(
                        self._con,
                        x,
                        y,
                        C_BLACK,
                        tcod.BKGND_SET
                    )
                    # However, if it has been explored set it to a dark colour
                    if game_map.map[x][y].explored:
                        if wall:
                            tcod.console_set_char_background(
                                self._con,
                                x,
                                y,
                                C_DARK_WALL,
                                tcod.BKGND_SET
                            )
                        else:
                            if game_map.map[x][y].stair[UP] or game_map.map[x][y].stair[DOWN]:
                                tcod.console_set_char_background(
                                    self._con,
                                    x,
                                    y,
                                    C_STAIR,
                                    tcod.BKGND_SET
                                )
                            else:
                                tcod.console_set_char_background(
                                    self._con,
                                    x,
                                    y,
                                    C_DARK_GROUND,
                                    tcod.BKGND_SET
                                )
                else:
                    # if the tile is visible because it lies in the FOV,
                    #  then paint it light
                    if wall:
                        tcod.console_set_char_background(self._con, x, y, C_LIGHT_WALL, tcod.BKGND_SET)
                    else:
                        if game_map.map[x][y].stair[UP] or game_map.map[x][y].stair[DOWN]:
                            tcod.console_set_char_background(
                                self._con,
                                x,
                                y,
                                C_LIGHT_STAIR,
                                tcod.BKGND_SET
                            )
                        else:
                            tcod.console_set_char_background(self._con, x, y, C_LIGHT_GROUND, tcod.BKGND_SET)
                    game_map.map[x][y].explored = True
    
    def render_gui(self, player, names_under_mouse):
        # show the player's stats
        tcod.console_set_default_foreground(self._con, tcod.white)

        # prepare to render the GUI panel
        tcod.console_set_default_background(self._panel, tcod.black)
        tcod.console_clear(self._panel)
 
        # print the game messages, one line at a time
        y = 1
        for (line, color) in self.logger.game_msgs:
            tcod.console_set_default_foreground(self._panel, color)
            tcod.console_print_ex(self._panel, MSG_X, y, tcod.BKGND_NONE, tcod.LEFT, line)
            y += 1

        #show the player's stats
        self.render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
            tcod.light_red, tcod.darker_red)
        # display names of objects under the mouse
        tcod.console_set_default_foreground(self._panel, tcod.light_gray)
        tcod.console_print_ex(self._panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, names_under_mouse)


    def render_all(self, objects, game_map, names_under_mouse, show_map_chars=False):
        # grab player
        player = list(filter(lambda x: x.is_player(), objects))[0]
        self.render_map(game_map, player, show_chars=show_map_chars)
        self.render_objects(objects, game_map)
        tcod.console_blit(self._con, 0, 0, self._width, self._height, 0, 0, 0)
        self.render_gui(player, names_under_mouse)
        # blit the contents of "panel" gui to the root console
        tcod.console_blit(self._panel, 0, 0, self._width, self._panel_height, 0, 0, PANEL_Y)
        tcod.console_flush()
        self.clear_objects(objects)
