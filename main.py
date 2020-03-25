import libtcodpy as tcod

from constants import *
from entities import *
from renderer import RenderScreen
from game_map import GameMap
from tile_loader import *

# FONT_PATH = 'arial10x10.png'
# FONT_PATH = 'tiles10x10.png'
# FONT_FLAGS = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD

def get_key_event(turn_based=None):
    if turn_based:
        # Turn-based game play; wait for a key stroke
        key = tcod.console_wait_for_keypress(True)
    else:
        # Real-time game play; don't wait for a player's key stroke
        key = tcod.console_check_for_keypress()
    return key

def main(turn_based):
    renderer = RenderScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Load custom tileset
    load_custom_font()
    
    # Game map
    game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)
    game_map.generate_map()
    player_pos = game_map.player_initial_pos
    
    # instantiate player
    # player = MainPlayer(player_pos[0], player_pos[1], '@', 'player', tcod.white, blocks=True)
    fighter_component = Fighter(hp=30, defense=2, power=5)
    player = MainPlayer(
        player_pos[0],
        player_pos[1],
        PLAYER_TILE,
        'player',
        tcod.white,
        blocks=True,
        fighter=fighter_component)
    
    # Game state and player's last action
    game_state = PLAYING
    player_action = None
    # Game loop
    while not tcod.console_is_window_closed():
        objects = game_map.level_objects + [player]
        key = get_key_event(turn_based)
        player_action = player.handle_keys(game_map, game_state, key)
        if key.vk == tcod.KEY_ENTER and key.lalt:
            #Alt+Enter: toggle fullscreen
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
        elif key.vk == tcod.KEY_ESCAPE:
            break  # exit game
        # let monsters take their turn if the player did
        if game_state == PLAYING and player_action != DIDNT_TAKE_TURN:
            for o in objects:
                if o != player:
                    o.ai.take_turn(game_map, player)
        renderer.render_all(objects, game_map, show_map_chars=False)

if __name__ == "__main__":
    # Game config
    turn_based = False
    # tcod.console_set_custom_font(FONT_PATH, FONT_FLAGS)
    tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, FULLSCREEN)
    tcod.sys_set_fps(LIMIT_FPS)
    main(turn_based)
