import libtcodpy as tcod

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, LIMIT_FPS, WINDOW_TITLE, FULLSCREEN
from player import MainPlayer
from renderer import RenderScreen

FONT_PATH = 'arial10x10.png'
FONT_FLAGS = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD

def get_key_event(turn_based=None):
    if turn_based:
        # Turn-based game play; wait for a key stroke
        key = tcod.console_wait_for_keypress(True)
    else:
        # Real-time game play; don't wait for a player's key stroke
        key = tcod.console_check_for_keypress()
    return key

def main(turn_based):
    renderer = RenderScreen()
    # instantiate player
    player = MainPlayer(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, '@')
    # Game loop
    while not tcod.console_is_window_closed():
        key = get_key_event(turn_based)
        if key.vk == tcod.KEY_ENTER and key.lalt:
            #Alt+Enter: toggle fullscreen
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
        elif key.vk == tcod.KEY_ESCAPE:
            return True  #exit game
        player.handle_keys(key)
        renderer.render([player])

if __name__ == "__main__":
    # Game config
    turn_based = False
    tcod.console_set_custom_font(FONT_PATH, FONT_FLAGS)
    tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, FULLSCREEN)
    tcod.sys_set_fps(LIMIT_FPS)
    main(turn_based)