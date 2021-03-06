# general config
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
WINDOW_TITLE = 'Python 3 libtcod tutorial'
FULLSCREEN = False

GAME_NAME = 'TOMBS OF THE ANCIENT KINGS'
AUTHOR = 'By Galloafro'

# map sizes
MAP_WIDTH = 80
MAP_HEIGHT = 43

# sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
INVENTORY_WIDTH = 50
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 30

# message log
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

# game states
PLAYING = 'playing'
DEAD = 'dead'

# main menu
NEW_GAME = 0
LOAD_GAME = 1
EXIT_GAME = 2

# player actions
DIDNT_TAKE_TURN = 'didnt_take_turn'
SHOW_INVENTORY = 'show_inventory'
DROP_ITEM = 'drop_item'
SHOW_STATUS = 'show_status'

# 
MAX_ITEMS = 26
MAX_MENU_OPTIONS = 26

# spawnable items
HEAL = 'heal'
LIGHTNING = 'lightning'
FIREBALL = 'fireball'
CONFUSE = 'confuse'
SWORD = 'sword'
SHIELD = 'shield'
# spawnable monsters
ORC = 'orc'
TROLL = 'troll'

# items
HEAL_AMOUNT = 4
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 12
CONFUSE_RANGE = 5

# Equipment slots
RIGHT_HAND = 'right hand'
LEFT_HAND = 'left hand'
HEAD = 'head'
BODY = 'body'

# experience and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150