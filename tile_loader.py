import libtcodpy as tcod

# Tiles source image
TILES_SOURCE = 'static/tiles10x10.png'
TILES_ROWS = 32
TILES_COLS = 8

# Give tiles a meaningful name
PLAYER_TILE = 33
ORC_TILE = 97
TROLL_TILE = 129

tcod.console_set_custom_font(TILES_SOURCE, tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD, TILES_ROWS, TILES_COLS)

def load_custom_font():
    # The index of the first custom tile in the file we will load
    a = 1
 
    # The "y" is the row index, here we load the sixth row in the font file. Increase the "6" to load any new rows from the file
    for y in range(0,TILES_COLS):
        # Remap a contiguous set of codes to a contiguous set of tiles.
        # tcod.console_map_ascii_codes_to_font(firstAsciiCode, nbCodes, fontCharX, fontCharY)
        tcod.console_map_ascii_codes_to_font(a, TILES_ROWS, 0, y)
        a += TILES_ROWS

