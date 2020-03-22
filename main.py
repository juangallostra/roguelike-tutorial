import libtcodpy as tcod
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, LIMIT_FPS, WINDOW_TITLE, FULLSCREEN

FONT_PATH = 'arial10x10.png'  # this will look in the same folder as this script
FONT_FLAGS = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD  # the layout may need to change with a different font file

def main():
    while not tcod.console_is_window_closed():
        pass

if __name__ == "__main__":
    tcod.console_set_custom_font(FONT_PATH, FONT_FLAGS)
    tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, FULLSCREEN)
    tcod.sys_set_fps(LIMIT_FPS)
    main()