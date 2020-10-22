import libtcodpy as tcod

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

# Give tiles a meaningful name
PLAYER_TILE = { True: OFFSET + 5, False: '@'}
ORC_TILE = { True: OFFSET + 11, False: 'O'}
TROLL_TILE = { True: OFFSET + 13, False: 'T'}
DAGGER_TILE = { True: '-', False: '-'}


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
