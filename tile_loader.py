import libtcodpy as tcod
from collections import namedtuple

FONT_PATH = 'static/test_font.png'
FONT_FLAGS = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD

# Tiles source image
TILES_SOURCE = 'static/complete_tileset.png'
TILES_ROWS = 20
TILES_COLS = 32
TILE_BEGINING_ROW = 5
TILE_END_ROW = 15

# The index of the first custom tile in the file we will load
OFFSET = 256

Tile = namedtuple('Tile', 'code color')
# Give tiles a meaningful name
PLAYER_TILE = { 
    True: Tile(code=OFFSET + 5, color=tcod.white), 
    False: Tile(code='@', color=tcod.white)
    }
ORC_TILE = { 
    True: Tile(code=OFFSET + 11, color=tcod.white),
    False: Tile(code='O', color=tcod.desaturated_green)
    }
TROLL_TILE = { 
    True: Tile(code=OFFSET + 13, color=tcod.white), 
    False: Tile(code='T', color=tcod.darker_green)
    }
DAGGER_TILE = { 
    True: Tile(code=OFFSET + TILES_COLS*4 + 10, color=tcod.white),
    False: Tile(code='-', color=tcod.sky)
    }
HEALING_POTION_TILE = {
    True: Tile(code=OFFSET + TILES_COLS*2 + 9, color=tcod.white),
    False: Tile(code='!', color=tcod.violet)
    }
SHIELD_TILE = {
    True: Tile(code=OFFSET + TILES_COLS*6 + 9, color=tcod.white),
    False: Tile(code='[', color=tcod.dark_orange)
}
SWORD_TILE = {
    True: Tile(code=OFFSET + TILES_COLS*4 + 6, color=tcod.white),
    False: Tile(code='/', color=tcod.sky)
}

def load_font(use_tiles=False):
    if not use_tiles:
        tcod.console_set_custom_font(FONT_PATH, FONT_FLAGS)
        return

    tcod.console_set_custom_font(TILES_SOURCE, FONT_FLAGS, TILES_COLS, TILES_ROWS)
    a = OFFSET
    # The "y" is the row index, here we load the sixth row in the font file. Increase the "6" to load any new rows from the file
    for y in range(TILE_BEGINING_ROW, TILE_END_ROW):
        # Remap a contiguous set of codes to a contiguous set of tiles.
        # tcod.console_map_ascii_codes_to_font(firstAsciiCode, nbCodes, fontCharX, fontCharY)
        tcod.console_map_ascii_codes_to_font(a, TILES_COLS, 0, y)
        a += TILES_COLS
