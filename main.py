import libtcodpy as tcod

from constants import *
from entities import *
from renderer import RenderScreen
from game_map import GameMap
from tile_loader import *

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

def get_names_under_mouse(mouse, game_map):
    # return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)
    # create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [
        obj.name for obj in game_map.level_objects 
        if obj.get_x_position() == x and obj.get_y_position() == y and tcod.map_is_in_fov(
            game_map.fov_map, 
            obj.get_x_position(), 
            obj.get_y_position()
        )
    ]
    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()

def main(turn_based):
    # system wide message logger
    logger = Logger()
    renderer = RenderScreen(SCREEN_WIDTH, SCREEN_HEIGHT, PANEL_HEIGHT, logger)
    
    # Load custom tileset
    # load_custom_font()
    
    # Game map
    game_map = GameMap(MAP_WIDTH, MAP_HEIGHT, logger=logger)
    game_map.generate_map()
    player_pos = game_map.player_initial_pos
    
    # instantiate player
    fighter_component = Fighter(hp=30, defense=2, power=5, death_function=player_death)
    player = MainPlayer(
        player_pos[0],
        player_pos[1],
        # PLAYER_TILE,
        '@',
        'player',
        tcod.white,
        blocks=True,
        fighter=fighter_component,
        logger=logger)
    
    # Game state and player's last action
    game_state = PLAYING
    player_action = None
    # Greet the player

    logger.log_message(
        'Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.',
        tcod.red
    )
    # Track mouse and keys
    mouse = tcod.Mouse()
    key = tcod.Key()
    # Limit FPS
    tcod.sys_set_fps(LIMIT_FPS)
    # Game loop
    while not tcod.console_is_window_closed():
        # check for events
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)
        # sort objects in level to draw first corpses
        game_map.level_objects = [
            o for o in game_map.level_objects if o.fighter is None
        ] + [
            o for o in game_map.level_objects if o.fighter is not None
        ]
        objects = game_map.level_objects + [player]
        # key = get_key_event(turn_based)
        player_action = player.handle_keys(game_map, game_state, key)
        if player_action == SHOW_INVENTORY:
                chosen_item = renderer.render_inventory_menu(
                    'Press the key next to an item to use it, or any other to cancel.\n',
                    player.inventory
                )
                if chosen_item is not None:
                    # player = kwargs['player']
                    # game_map = kwargs['game_map']
                    # renderer = kwargs['renderer']
                    # names_under_mouse = kwargs['names_under_mouse']
                    # show_map_chars = kwargs['show_map_chars']
                    # mouse = kwargs['mouse']
                    # key = kwargs['key']
                    chosen_item.use(
                        player.inventory, 
                        player=player, 
                        game_map=game_map,
                        mouse=mouse,
                        renderer=renderer,
                        key=key,
                        names_under_mouse=get_names_under_mouse(mouse, game_map),
                        show_map_chars=False
                    )
        if key.vk == tcod.KEY_ENTER and key.lalt:
            #Alt+Enter: toggle fullscreen
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
        elif key.vk == tcod.KEY_ESCAPE:
            break  # exit game
        # let monsters take their turn if the player did
        if game_state == PLAYING and player_action != DIDNT_TAKE_TURN:
            for o in objects:
                if o != player and o.ai:
                    o.ai.take_turn(game_map, player)
        # Update game state with player death
        game_state = player.state
        names_under_mouse = get_names_under_mouse(mouse, game_map)
        renderer.render_all(objects, game_map, names_under_mouse, show_map_chars=False)

if __name__ == "__main__":
    # Game config
    turn_based = False
    tcod.console_set_custom_font(FONT_PATH, FONT_FLAGS)
    tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, FULLSCREEN)
    tcod.sys_set_fps(LIMIT_FPS)
    main(turn_based)
