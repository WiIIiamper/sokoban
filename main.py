import pyray as raylib
import sokoban
import editor

if __name__ == '__main__':
    screen_width = 1280
    screen_height = 720
    raylib.set_config_flags(raylib.ConfigFlags.FLAG_MSAA_4X_HINT)
    raylib.init_window(screen_width, screen_height, 'Sokoban')
    raylib.set_target_fps(60)
    
    #TODO: Implement different modes
    class ProgarmModes():
        GAME = 0
        EDITOR = 1
        MENU = 2
    program_mode = ProgarmModes.GAME

    sokoban.init_sokoban()
    while not raylib.window_should_close():
        #TOGGLE EDITOR
        if sokoban.IS_DEBUG_RUN and raylib.is_key_pressed(raylib.KeyboardKey.KEY_F5):
            if program_mode == ProgarmModes.GAME:
                program_mode = ProgarmModes.EDITOR
                editor.init_editor()
            elif program_mode == ProgarmModes.EDITOR:
                program_mode = ProgarmModes.GAME 
                sokoban.init_sokoban()

        #UPDATE
        if program_mode == ProgarmModes.GAME:
            sokoban.update()
        elif program_mode == ProgarmModes.EDITOR:
            editor.update()

        #DRAW
        raylib.begin_drawing()
        raylib.clear_background(raylib.BLACK)

        if program_mode == ProgarmModes.GAME:
            sokoban.draw()
        elif program_mode == ProgarmModes.EDITOR:
            editor.draw()

        raylib.end_drawing()

    raylib.close_window()