import pyray as raylib
import sokoban

mode = 0
SELECT_STARTING_TILE_MODE = 1337
PUT_STORAGE_LOC_MODE = 9984

view_level = 0
levels = []

def init_editor():
    global view_level, levels, mode
    view_level = 0
    mode = 0
    levels = sokoban.load_levels_from_disk()

def get_tile_size() -> int:
    level_view_width = raylib.get_screen_width() * 0.7
    level_view_height = raylib.get_screen_height()
    tile_width = level_view_width / levels[view_level].columns
    tile_height = level_view_height / levels[view_level].rows
    return int( min(tile_width, tile_height) )

def save_levels_to_disk():
    f = open("levels", "w")

    f.write(str(len(levels)) + '\n')
    for i in range(len(levels)):
        f.write(str(levels[i].rows) + ' ' + str(levels[i].columns) + '\n')
        f.write(str(levels[i].starting_pos.x) + ' ' + str(levels[i].starting_pos.y) + '\n')

        for row in range(levels[i].rows):
            for col in range(levels[i].columns):
                f.write(str(levels[i].tiles[row][col]) + ' ')
            f.write('\n')
        for row in range(levels[i].rows):
            for col in range(levels[i].columns):
                f.write(str(levels[i].is_storage_loc[row][col]) + ' ')
            f.write('\n')

        if raylib.vector3_equals(levels[i].camera_position, raylib.vector3_zero()):
            levels[i].camera_position.x = levels[i].columns * 0.5
            levels[i].camera_position.y = 10
            levels[i].camera_position.z = levels[i].rows * 0.55

        f.write(str(levels[i].camera_position.x) + ' ' + str(levels[i].camera_position.y) + ' ' + str(levels[i].camera_position.z) + '\n')

    f.close()

def update():
    global view_level
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_RIGHT):
        view_level += 1
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_LEFT):
        view_level -= 1
    if view_level >= len(levels):
        view_level = 0
    if view_level < 0:
        view_level = len(levels)-1

    #INSERT NEW LEVEL
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_N):
        levels.insert(view_level+1, sokoban.SokobanLevel())
        view_level += 1
        levels[view_level].rows = 1
        levels[view_level].columns = 1
        levels[view_level].tiles = [[0]]
        levels[view_level].is_storage_loc = [[0]]

    #DELETE LEVEL
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_DELETE) and len(levels) >= 1:
        levels.pop(view_level)
        if (view_level >= len(levels)):
            view_level -= 1
    
    #SELECT MODE
    global mode
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_ZERO):
        mode = 0
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_ONE):
        mode = 1
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_TWO):
        mode = 2
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_THREE):
        mode = 3
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_X):
        mode = SELECT_STARTING_TILE_MODE
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_C):
        mode = PUT_STORAGE_LOC_MODE

    #RESIZE LEVEL
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_S):
        levels[view_level].rows += 1
        levels[view_level].tiles.append( [0]*levels[view_level].columns )
        levels[view_level].is_storage_loc.append( [0]*levels[view_level].columns )
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_W):
        if levels[view_level].rows > 1:
            levels[view_level].rows -= 1
            levels[view_level].tiles.pop()
            levels[view_level].is_storage_loc.pop()
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_D):
        levels[view_level].columns += 1
        for row in levels[view_level].tiles:
            row.append(0)
        for row in levels[view_level].is_storage_loc:
            row.append(0)
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_A):
        if levels[view_level].columns > 1:
            levels[view_level].columns -= 1
            for row in levels[view_level].tiles:
                row.pop()
            for row in levels[view_level].is_storage_loc:
                row.pop()

    #EDIT THE TILES
    if raylib.is_mouse_button_pressed(raylib.MouseButton.MOUSE_BUTTON_LEFT):
        mouse_pos = raylib.get_mouse_position()
        tile_size = get_tile_size()
        tile_clicked_x = int(mouse_pos.x / tile_size)
        tile_clicked_y = int(mouse_pos.y / tile_size)
        
        if (
            tile_clicked_x >= 0 and tile_clicked_x < levels[view_level].columns and
            tile_clicked_y >= 0 and tile_clicked_y < levels[view_level].rows
        ):
            if (
                mode == sokoban.TileTypes.VOID or mode == sokoban.TileTypes.EMPTY or
                mode == sokoban.TileTypes.WALL or mode == sokoban.TileTypes.BOX
            ):
                levels[view_level].tiles[tile_clicked_y][tile_clicked_x] = mode
            elif mode == PUT_STORAGE_LOC_MODE: # TOGGLE 'STORAGE LOCTION' BOOLEAN
                levels[view_level].is_storage_loc[tile_clicked_y][tile_clicked_x] = (1 - levels[view_level].is_storage_loc[tile_clicked_y][tile_clicked_x])
            elif mode == SELECT_STARTING_TILE_MODE:
                levels[view_level].starting_pos = sokoban.Vec2i(tile_clicked_x, tile_clicked_y)

    #SAVE
    if raylib.is_key_pressed(raylib.KeyboardKey.KEY_ENTER):
        save_levels_to_disk()

def draw():
    global mode
    tile_size = get_tile_size()

    #Draw the level tiles
    y : int = 0
    for row in range(levels[view_level].rows):
        x : int = 0
        for col in range(levels[view_level].columns):
            tile_type = levels[view_level].tiles[row][col]
            if tile_type == sokoban.TileTypes.EMPTY:
                raylib.draw_rectangle(int(x), int(y), tile_size, tile_size, raylib.LIGHTGRAY)
            elif tile_type == sokoban.TileTypes.WALL:
                raylib.draw_rectangle(int(x), int(y), tile_size, tile_size, raylib.GRAY)
            elif tile_type == sokoban.TileTypes.BOX:
                raylib.draw_rectangle(int(x), int(y), tile_size, tile_size, raylib.ORANGE)

            if mode == PUT_STORAGE_LOC_MODE or mode == SELECT_STARTING_TILE_MODE:
                if levels[view_level].is_storage_loc[row][col]:
                    raylib.draw_rectangle(int(x), int(y), tile_size, tile_size, raylib.RED)
                elif row == levels[view_level].starting_pos.y and col == levels[view_level].starting_pos.x:
                    raylib.draw_rectangle(int(x), int(y), tile_size, tile_size, raylib.BLUE)

            raylib.draw_rectangle_lines(int(x), int(y), tile_size, tile_size, raylib.WHITE)
            x += tile_size
        y += tile_size

    sidebar_x = int(raylib.get_screen_width() * 0.7)
    raylib.draw_text('Level ' + str(view_level+1) + '/' + str(len(levels)), sidebar_x, 10, 24, raylib.WHITE)
    raylib.draw_text('N to insert, DELETE to delete', sidebar_x, 34, 20, raylib.WHITE)

    raylib.draw_text('Mode:', sidebar_x, 57, 20, raylib.WHITE)
    if mode == sokoban.TileTypes.VOID:
        raylib.draw_text('PUT VOID', sidebar_x + 60, 57, 20, raylib.RED)
    elif mode == sokoban.TileTypes.EMPTY:
        raylib.draw_text('PUT EMPTY', sidebar_x + 60, 57, 20, raylib.GREEN)
    elif mode == sokoban.TileTypes.WALL:
        raylib.draw_text('PUT WALL', sidebar_x + 60, 57, 20, raylib.GRAY)
    elif mode == sokoban.TileTypes.BOX:
        raylib.draw_text('PUT BOX', sidebar_x + 60, 57, 20, raylib.ORANGE)
    elif mode == PUT_STORAGE_LOC_MODE:
        raylib.draw_text('PUT STORAGE LOCATION', sidebar_x + 60, 57, 20, raylib.PINK)
    elif mode == SELECT_STARTING_TILE_MODE:
        raylib.draw_text('SELECT START', sidebar_x + 60, 57, 20, raylib.BLUE)

    raylib.draw_text('Press 0,1,2,3,X,C to change mode', sidebar_x, 81, 20, raylib.WHITE)
    raylib.draw_text('Puzzle Rows ' + str(levels[view_level].rows) + ' Columns' + str(levels[view_level].columns), sidebar_x, 115, 20, raylib.WHITE)
    raylib.draw_text('WASD to resize puzzle', sidebar_x, 139, 20, raylib.WHITE)