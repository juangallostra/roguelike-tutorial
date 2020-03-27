# general config
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
WINDOW_TITLE = 'Python 3 libtcod tutorial'
FULLSCREEN = False

# map sizes
MAP_WIDTH = 80
MAP_HEIGHT = 43

# sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
INVENTORY_WIDTH = 50

# message log
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

# game states
PLAYING = 'playing'
DEAD = 'dead'

# player actions
DIDNT_TAKE_TURN = 'didnt_take_turn'
SHOW_INVENTORY = 'show_inventory'

# 
MAX_ITEMS = 26
MAX_MENU_OPTIONS = 26