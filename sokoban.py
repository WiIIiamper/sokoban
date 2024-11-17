import pyray as raylib

IS_DEBUG_RUN = False

class Vec2i():
    def __init__(self, x,y):
        self.x = int(x)
        self.y = int(y)

class SokobanLevel():
    def __init__(self):
        self.rows = 0
        self.columns = 0
        self.starting_pos = Vec2i(0,0)
        self.tiles = []
        self.is_storage_loc = []  
        self.camera_position = raylib.vector3_zero()
        # self.light_dir = raylib.vector3_zero() #NOTE: May need this at some point

levels = []
current_level = 0

class TileTypes():
    VOID = 0
    EMPTY = 1
    WALL = 2
    BOX = 3

puzzle_rows = 0
puzzle_columns = 0
tiles = []
is_storage_loc = []

player_tile = Vec2i(0, 0)
player_pos = raylib.vector3_zero()
camera = raylib.Camera3D()

class Move():
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3

    def __init__(self, dir: int, pushed_box: bool):
        self.dir = dir
        self.pushed_box = pushed_box

move_stack = []

def load_levels_from_disk():
    levels = []
    with open('levels') as f:
        num_levels = int(next(f))
        for lvl in range(num_levels):
            levels.append(SokobanLevel())

            line = next(f).split()
            levels[-1].rows = int(line[0])
            levels[-1].columns = int(line[1])
            line = next(f).split()
            levels[-1].starting_pos = Vec2i(int(line[0]), int(line[1]))

            for row in range(levels[-1].rows):
                levels[-1].tiles.append([])
                line = next(f).split()
                for tile in line:
                    levels[-1].tiles[row].append(int(tile))
            
            for row in range(levels[-1].rows):
                levels[-1].is_storage_loc.append([])
                line = next(f).split()
                for tile in line:
                    levels[-1].is_storage_loc[row].append(int(tile))

            line = next(f).split()
            levels[-1].camera_position = raylib.Vector3(float(line[0]), float(line[1]), float(line[2]))
    return levels

def init_level(level_idx):
    global puzzle_rows, puzzle_columns, player_tile, player_pos
    global tiles, is_storage_loc, camera, move_stack

    puzzle_rows = levels[level_idx].rows
    puzzle_columns = levels[level_idx].columns
    player_tile = levels[level_idx].starting_pos
    tiles = levels[level_idx].tiles
    is_storage_loc = levels[level_idx].is_storage_loc

    player_pos = raylib.Vector3(player_tile.x, 1, player_tile.y)

    camera.target = [puzzle_columns * 0.5, 0, puzzle_rows * 0.5]
    camera.position = levels[level_idx].camera_position
    
    move_stack = []

def init_sokoban():
    global levels
    levels = load_levels_from_disk()

    #Initialize Camera
    camera.up = (0, 1, 0)
    camera.projection = raylib.CameraProjection.CAMERA_PERSPECTIVE
    camera.fovy = 90

    global current_level
    current_level = 0
    init_level(current_level)

def is_key_being_pressed(key):
    return raylib.is_key_pressed(key) or raylib.is_key_pressed_repeat(key)

def is_valid_tile(y, x): 
    return y >= 0 and y < puzzle_rows and x >= 0 and x < puzzle_columns

def is_empty_tile(y, x):
    if not is_valid_tile(y,x):
        return False
    
    return tiles[int(y)][int(x)] == TileTypes.EMPTY

def is_box_tile(y, x):
    if not is_valid_tile(y,x):
        return False

    return tiles[int(y)][int(x)] == TileTypes.BOX

def can_move_up():
    if (
        not is_key_being_pressed(raylib.KeyboardKey.KEY_W) and
        not is_key_being_pressed(raylib.KeyboardKey.KEY_UP)
    ):
        return False
    if not is_empty_tile(player_tile.y - 1, player_tile.x):
        if not is_box_tile(player_tile.y-1, player_tile.x):
            return False
        if not is_empty_tile(player_tile.y-2, player_tile.x):
            return False
    return True

def can_move_down():
    if (
        not is_key_being_pressed(raylib.KeyboardKey.KEY_S) and
        not is_key_being_pressed(raylib.KeyboardKey.KEY_DOWN)
    ):
        return False
    if not is_empty_tile(player_tile.y + 1, player_tile.x):
        if not is_box_tile(player_tile.y + 1, player_tile.x):
            return False
        if not is_empty_tile(player_tile.y + 2, player_tile.x):
            return False
    return True

def can_move_left():
    if (
        not is_key_being_pressed(raylib.KeyboardKey.KEY_A) and
        not is_key_being_pressed(raylib.KeyboardKey.KEY_LEFT)
    ):
        return False
    if not is_empty_tile(player_tile.y, player_tile.x-1):
        if not is_box_tile(player_tile.y, player_tile.x-1):
            return False
        if not is_empty_tile(player_tile.y, player_tile.x-2):
            return False
    return True

def can_move_right():
    if (
        not is_key_being_pressed(raylib.KeyboardKey.KEY_D) and
        not is_key_being_pressed(raylib.KeyboardKey.KEY_RIGHT)
    ):
        return False
    if not is_empty_tile(player_tile.y, player_tile.x+1):
        if not is_box_tile(player_tile.y, player_tile.x+1):
            return False
        if not is_empty_tile(player_tile.y, player_tile.x+2):
            return False
    return True

def undo_move():
    if len(move_stack) > 0:
        if move_stack[-1].dir == Move.UP:
            if move_stack[-1].pushed_box == True:
                tiles[player_tile.y][player_tile.x] = TileTypes.BOX
                tiles[player_tile.y-1][player_tile.x] = TileTypes.EMPTY

            player_tile.y += 1
        elif move_stack[-1].dir == Move.LEFT:
            if move_stack[-1].pushed_box == True:
                tiles[player_tile.y][player_tile.x] = TileTypes.BOX
                tiles[player_tile.y][player_tile.x-1] = TileTypes.EMPTY

            player_tile.x += 1
        elif move_stack[-1].dir == Move.DOWN:
            if move_stack[-1].pushed_box == True:
                tiles[player_tile.y][player_tile.x] = TileTypes.BOX
                tiles[player_tile.y+1][player_tile.x] = TileTypes.EMPTY

            player_tile.y -= 1
        elif move_stack[-1].dir == Move.RIGHT:
            if move_stack[-1].pushed_box == True:
                tiles[player_tile.y][player_tile.x] = TileTypes.BOX
                tiles[player_tile.y][player_tile.x+1] = TileTypes.EMPTY
            
            player_tile.x -= 1
        
        move_stack.pop()

def is_level_finished():
    for row in range(puzzle_rows):
        for col in range(puzzle_columns):
            if is_storage_loc[row][col] and not is_box_tile(row, col):
                return False
    return True

def update_player_tile_based_on_input():
    #NOTE: The player can only move NORTH SOUTH EAST WEST
    if can_move_up():
        player_tile.y -= 1

        if is_box_tile(player_tile.y, player_tile.x):
            tiles[player_tile.y][player_tile.x] = TileTypes.EMPTY
            tiles[player_tile.y-1][player_tile.x] = TileTypes.BOX
            move_stack.append(Move(Move.UP, True))
        else:
            move_stack.append(Move(Move.UP, False))
    elif can_move_left():
        player_tile.x -= 1

        if is_box_tile(player_tile.y, player_tile.x):
            tiles[player_tile.y][player_tile.x] = TileTypes.EMPTY
            tiles[player_tile.y][player_tile.x-1] = TileTypes.BOX
            move_stack.append(Move(Move.LEFT, True))
        else:
            move_stack.append(Move(Move.LEFT, False))
    elif can_move_down():
        player_tile.y += 1

        if is_box_tile(player_tile.y, player_tile.x):
            tiles[player_tile.y][player_tile.x] = TileTypes.EMPTY
            tiles[player_tile.y+1][player_tile.x] = TileTypes.BOX
            move_stack.append(Move(Move.DOWN, True))
        else:
            move_stack.append(Move(Move.DOWN, False))
    elif can_move_right():
        player_tile.x += 1

        if is_box_tile(player_tile.y, player_tile.x):
            tiles[player_tile.y][player_tile.x] = TileTypes.EMPTY
            tiles[player_tile.y][player_tile.x+1] = TileTypes.BOX
            move_stack.append(Move(Move.RIGHT, True))
        else:
            move_stack.append(Move(Move.RIGHT, False))

def update():
    global current_level
    #NOTE:Temporary solution untill we have a menu
    if current_level < len(levels)-1 and raylib.is_key_pressed(raylib.KeyboardKey.KEY_PAGE_UP):
        current_level += 1
        init_level(current_level)
        return
    if current_level > 0 and raylib.is_key_pressed(raylib.KeyboardKey.KEY_PAGE_DOWN):
        current_level -= 1
        init_level(current_level)
        return

    if not is_level_finished():
        if is_key_being_pressed(raylib.KeyboardKey.KEY_SPACE):
            undo_move()
        if is_key_being_pressed(raylib.KeyboardKey.KEY_R):
            while len(move_stack) > 0:
                undo_move()
        update_player_tile_based_on_input()
    else:
        if current_level < len(levels)-1 and raylib.is_key_pressed(raylib.KeyboardKey.KEY_ENTER):
            current_level += 1
            init_level(current_level)
            return
    
    global player_pos
    player_delta = raylib.vector3_subtract(raylib.Vector3(player_tile.x, 1, player_tile.y), player_pos)
    player_pos = raylib.vector3_add(player_pos, raylib.vector3_scale(player_delta, 15 * raylib.get_frame_time()))


def draw():
    raylib.begin_mode_3d(camera)

    for row in range(puzzle_rows):
        for column in range(puzzle_columns):
            tile_pos = raylib.Vector3(column, 0, row)
            tile_type = tiles[row][column]

            if tile_type == TileTypes.VOID:
                continue 
            elif tile_type == TileTypes.EMPTY:
                if is_storage_loc[row][column]:
                    raylib.draw_cube(tile_pos, 1, 1, 1, raylib.Color(255,100,120,255))
                else:
                    raylib.draw_cube(tile_pos, 1, 1, 1, raylib.LIGHTGRAY)

                raylib.draw_cube_wires(tile_pos, 1, 1, 1, raylib.YELLOW)
            elif tile_type == TileTypes.WALL:
                tile_pos.y += 1
                raylib.draw_cube(tile_pos, 1, 1, 1, raylib.GRAY)
                raylib.draw_cube_wires(tile_pos, 1, 1, 1, raylib.YELLOW)
            elif tile_type == TileTypes.BOX:
                #First draw the tile under the box
                if is_storage_loc[row][column]:
                    raylib.draw_cube(tile_pos, 1, 1, 1, raylib.Color(255,100,120,255))
                else:
                    raylib.draw_cube(tile_pos, 1, 1, 1, raylib.LIGHTGRAY)
                raylib.draw_cube_wires(tile_pos, 1, 1, 1, raylib.YELLOW)
                tile_pos.y += 1

                if is_storage_loc[row][column]:
                    raylib.draw_cube(tile_pos, 0.8, 0.8, 0.8, raylib.Color(255, 100, 0, 255))
                else:
                    raylib.draw_cube(tile_pos, 0.8, 0.8, 0.8, raylib.ORANGE)
                raylib.draw_cube_wires(tile_pos, 0.8, 0.8, 0.8, raylib.YELLOW)

    global player_pos
    raylib.draw_cube(player_pos, 0.8, 0.8, 0.8, raylib.BLUE)

    raylib.end_mode_3d()

    #TODO: Maybe have a global variable for is_level_finished
    if is_level_finished():
        if current_level == len(levels)-1:
            raylib.draw_text('You have completed all the levels. Tell NASA to hire you.', 10, 10, 24, raylib.RED)
        else:
            raylib.draw_text('You have completed this level. Press ENTER to go to the next one.', 10, 10, 24, raylib.RED)

    # Draw Debug Info
    if IS_DEBUG_RUN:
        raylib.draw_text('Player Tile ' + str(player_tile.y) + ' ' + str(player_tile.x), 10, 10, 16, raylib.GREEN)
        raylib.draw_text('Camera Pos ' + str(round(camera.position.x, 2)) + ' ' 
                                       + str(round(camera.position.y, 2)) + ' ' 
                                       + str(round(camera.position.z, 2)), 10, 31, 16, raylib.GREEN)
        raylib.draw_text('Move stack size ' + str(len(move_stack)), 10, 52, 16, raylib.GREEN)