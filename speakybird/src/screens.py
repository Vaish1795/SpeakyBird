import sys
from threading import active_count
import numpy as np
import pygame as pg
import global_var

from sprites import BirdWalk, Bird
from game import Game
from game_initializer import GameInitializer
from supporter import show_score, save_to_csv, load_leaderboard, load_avatar
from ui_elements import Button, update_level_button_images, TextInput


class Screens(GameInitializer):
    def __init__(self, model_arg, plot_transcribe_time, settings, constants):
        super().__init__(settings, constants)
        self.bird = Bird(self.settings, self.constants, self.bird_sprites, self.bird_image, self.base, self.sounds)

        self.bird_stairs = BirdWalk(self.settings, self.constants, self.bird_stairs_sprites, self.bird_stair_image, self.base, self.sounds, 0, 0)

        # self.model = model
        self.plot_transcribe_time = plot_transcribe_time
        self.set_speech_recognition_model(model_arg, self.plot_transcribe_time)

        self.sound_button = None
        self.language_button = None
        self.keyboard_button = None
        self.voice_button = None
        self.level_pipe_button = None
        self.level_fireball_button = None
        self.leaderboard_button = None

        self.level_combine_button = None

        self.alpha_value = 150
        self.is_on = False  # Initialize toggle state

        self.welcome = self.images['welcome']
        self.bird_image = self.bird_image[0]

        self.buttons = []
        self.pipe_button_state = 'disabled'
        self.fireball_button_state = 'disabled'

        self.combined_button_state = 'disabled'

        self.play_button = None
        self.settings_button = None
        self.leaderboard_button = None
        self.quit_button = None

        # buttons for user profile
        self.next_button = None
        self.prev_button = None
        self.user_profile_button = None

        self.name = global_var.name
        self.current_avatar = global_var.current_avatar
        self.avatar = None
        self.user_name = None

        self.pipe_level_surface, self.pipe_level_surface_rect, self.level_pipe = None, None, None
        self.fireball_level_surface, self.fireball_level_surface_rect, self.level_fireball = None, None, None

        # self.staircase_level_surface, self.staircase_level_surface_rect, self.level_staircase = None, None, None
        self.combine_level_surface, self.combine_level_surface_rect, self.level_combine = None, None, None

        self.game = Game(model_arg, self.plot_transcribe_time, self.transcriber, self, settings, constants, self.shared_data)


    def settings_screen(self):
        settings_title = self.settings.title_font.render('Settings', True, (255, 255, 255))
        settings_title_rect = settings_title.get_rect()
        settings_inner_rect = pg.Surface((self.settings.game_screen_width, self.settings.game_screen_height),
                                         pg.SRCALPHA)
        settings_inner_rect.fill((102, 153, 204, self.alpha_value))

        inner_rect = settings_inner_rect.get_rect()

        settings_options_text_pos = (
            (inner_rect.topright[0] + inner_rect.midtop[0]) // 2, settings_title_rect.bottom + 150)

        toggle_button_pos = (settings_options_text_pos[0] + 150, settings_options_text_pos[1])

        # Sound
        item_name = self.settings.settings_options_font.render('Sound', True, (255, 255, 255))
        item_rect = item_name.get_rect(midleft=(settings_options_text_pos[0] - 200, settings_options_text_pos[1]))

        # Language
        lang_item_name = self.settings.settings_options_font.render('Language', True, (255, 255, 255))
        lang_item_rect = lang_item_name.get_rect(
            midleft=(settings_options_text_pos[0] - 200, settings_options_text_pos[1] + 50))

        # banner right : Input mode
        banner = pg.Surface((inner_rect.midtop[0] - 150, 50), pg.SRCALPHA, 32)
        banner_rect = banner.get_rect(
            center=(settings_options_text_pos[0], settings_options_text_pos[1] + 150))
        banner.fill((115, 147, 179, self.alpha_value))

        input_mode_title = self.settings.subtitle_font.render('Mode', True, (255, 255, 255))
        input_mode_rect = input_mode_title.get_rect(center=(banner_rect.centerx, banner_rect.centery))

        # Input mode options Keyboard
        input_mode_keyboard_text = self.settings.settings_options_font.render('Keyboard', True, (255, 255, 255))
        input_mode_keyboard_rect = input_mode_keyboard_text.get_rect(
            midleft=(settings_options_text_pos[0] - 200, banner_rect.bottom + 50))

        # Input mode options Voice
        input_mode_voice_text = self.settings.settings_options_font.render('Voice', True, (255, 255, 255))
        input_mode_voice_rect = input_mode_voice_text.get_rect(
            midleft=(settings_options_text_pos[0] - 200, banner_rect.bottom + 100))

        # right side measurements
        settings_options_text_pos_right = (
            (inner_rect.topleft[0] + inner_rect.midtop[0]) // 2, settings_title_rect.bottom + 150)

        # banner left : Levels
        banner_left = pg.Surface((inner_rect.midtop[0] - 150, 50), pg.SRCALPHA, 32)
        banner_left_rect = banner_left.get_rect(
            midleft=(settings_options_text_pos_right[0] - 200, settings_options_text_pos_right[1]))
        banner_left.fill((115, 147, 179, self.alpha_value))

        levels_title = self.settings.subtitle_font.render('Levels', True, (255, 255, 255))
        levels_rect = levels_title.get_rect(center=(banner_left_rect.centerx, banner_left_rect.centery))

        self.pipe_level_surface, self.pipe_level_surface_rect, self.level_pipe = (
            self.create_level_layout(banner_left_rect.left, banner_left_rect.bottom + 50, 'Pipes'))
        self.fireball_level_surface, self.fireball_level_surface_rect, self.level_fireball = (
            self.create_level_layout(banner_left_rect.left + 350, banner_left_rect.bottom + 50, 'Fireball'))

        self.combine_level_surface, self.combine_level_surface_rect, self.level_combine = (
            self.create_level_layout(banner_left_rect.left, banner_left_rect.bottom + 150, 'Combined'))


        # Buttons
        self.sound_button = Button(self.settings, self.constants, self.images['toggle_on'], toggle_button_pos[0],
                                   toggle_button_pos[1], '')
        self.language_button = Button(self.settings, self.constants, self.images['english'], toggle_button_pos[0],
                                      toggle_button_pos[1] + 50, '')
        self.keyboard_button = Button(self.settings, self.constants, self.images['toggle_off'], toggle_button_pos[0],
                                      banner_rect.bottom + 50, '')
        self.voice_button = Button(self.settings, self.constants, self.images['toggle_on'], toggle_button_pos[0],
                                   banner_rect.bottom + 100, '')
        self.level_pipe_button = Button(self.settings, self.constants, self.pipe_level_surface,
                                        self.pipe_level_surface_rect.centerx, self.pipe_level_surface_rect.centery,
                                        'Pipes')
        self.level_fireball_button = Button(self.settings, self.constants, self.fireball_level_surface,
                                            self.fireball_level_surface_rect.centerx,
                                            self.fireball_level_surface_rect.centery,
                                            'Fireball')
        self.level_combine_button = Button(self.settings, self.constants, self.combine_level_surface,
                                           self.combine_level_surface_rect.centerx,
                                           self.combine_level_surface_rect.centery,
                                           'Combined')


        if global_var.level_settings.get_setting('sound'):
            self.sound_button.update_image(self.images['toggle_on'])
        else:
            self.sound_button.update_image(self.images['toggle_off'])

        if global_var.level_settings.get_setting('voice'):
            self.voice_button.update_image(self.images['toggle_on'])
            self.keyboard_button.update_image(self.images['toggle_off'])

        if global_var.level_settings.get_setting('keyboard'):
            self.keyboard_button.update_image(self.images['toggle_on'])
            self.voice_button.update_image(self.images['toggle_off'])

        if global_var.level_settings.get_setting('pipes'):
            update_level_button_images(self.level_pipe_button, self.alpha_value, 'enabled')
            update_level_button_images(self.level_fireball_button, self.alpha_value, 'disabled')
            update_level_button_images(self.level_combine_button, self.alpha_value, 'disabled')

        if global_var.level_settings.get_setting('fireball'):
            update_level_button_images(self.level_fireball_button, self.alpha_value, 'enabled')
            update_level_button_images(self.level_pipe_button, self.alpha_value, 'disabled')
            update_level_button_images(self.level_combine_button, self.alpha_value, 'disabled')

        if global_var.level_settings.get_setting('combined'):
            update_level_button_images(self.level_combine_button, self.alpha_value, 'enabled')
            update_level_button_images(self.level_pipe_button, self.alpha_value, 'disabled')
            update_level_button_images(self.level_fireball_button, self.alpha_value, 'disabled')
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.sound_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        self.is_on = not self.is_on  # Toggle the state
                        if self.is_on:
                            self.sound_button.update_image(self.images['toggle_on'])
                            global_var.level_settings.set_setting("sound", True)
                        else:
                            self.sound_button.update_image(self.images['toggle_off'])
                            global_var.level_settings.set_setting("sound", False)

                    if self.language_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        self.is_on = not self.is_on  # Toggle the state
                        if self.is_on:
                            self.language_button.update_image(self.images['german'])
                            global_var.level_settings.set_setting("language", "german")
                        else:
                            self.language_button.update_image(self.images['english'])
                            global_var.level_settings.set_setting("language", "english")

                    if self.keyboard_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        self.is_on = not self.is_on  # Toggle the state
                        if self.is_on:
                            self.keyboard_button.update_image(self.images['toggle_on'])
                            self.voice_button.update_image(self.images['toggle_off'])
                            global_var.level_settings.set_setting("keyboard", True)
                            global_var.level_settings.set_setting("voice", False)
                        else:
                            self.keyboard_button.update_image(self.images['toggle_off'])
                            self.voice_button.update_image(self.images['toggle_on'])
                            global_var.level_settings.set_setting("keyboard", False)
                            global_var.level_settings.set_setting("voice", True)

                    if self.voice_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        self.is_on = not self.is_on  # Toggle the state
                        if self.is_on:
                            self.voice_button.update_image(self.images['toggle_on'])
                            self.keyboard_button.update_image(self.images['toggle_off'])
                            global_var.level_settings.set_setting("voice", True)
                            global_var.level_settings.set_setting("keyboard", False)
                        else:
                            self.voice_button.update_image(self.images['toggle_off'])
                            self.keyboard_button.update_image(self.images['toggle_on'])
                            global_var.level_settings.set_setting("voice", False)
                            global_var.level_settings.set_setting("keyboard", True)

                    if self.level_pipe_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        if self.pipe_button_state == 'disabled':
                            update_level_button_images(self.level_pipe_button, self.alpha_value, 'enabled')
                            update_level_button_images(self.level_fireball_button, self.alpha_value, 'disabled')
                            update_level_button_images(self.level_combine_button, self.alpha_value, 'disabled')
                            global_var.level_settings.set_setting("pipes", True)
                            global_var.level_settings.set_setting("fireball", False)
                            global_var.level_settings.set_setting("combined", False)
                        else:
                            update_level_button_images(self.level_pipe_button, self.alpha_value, 'disabled')
                            update_level_button_images(self.level_fireball_button, self.alpha_value, 'enabled')
                            update_level_button_images(self.level_combine_button, self.alpha_value, 'disabled')
                            global_var.level_settings.set_setting("pipes", False)
                            self.pipe_button_state = 'disabled'

                    if self.level_fireball_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        if self.fireball_button_state == 'disabled':
                            update_level_button_images(self.level_fireball_button, self.alpha_value, 'enabled')
                            update_level_button_images(self.level_pipe_button, self.alpha_value, 'disabled')
                            update_level_button_images(self.level_combine_button, self.alpha_value, 'disabled')
                            global_var.level_settings.set_setting("fireball", True)
                            global_var.level_settings.set_setting("pipes", False)
                            global_var.level_settings.set_setting("combined", False)
                        else:
                            update_level_button_images(self.level_fireball_button, self.alpha_value, 'disabled')
                            update_level_button_images(self.level_pipe_button, self.alpha_value, 'enabled')
                            update_level_button_images(self.level_combine_button, self.alpha_value, 'disabled')
                            global_var.level_settings.set_setting("fireball", False)
                            self.fireball_button_state = 'disabled'

                    if self.level_combine_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        if self.combined_button_state == 'disabled':
                            update_level_button_images(self.level_combine_button, self.alpha_value,
                                                       'enabled')
                            update_level_button_images(self.level_fireball_button, self.alpha_value, 'disabled')
                            update_level_button_images(self.level_pipe_button, self.alpha_value, 'disabled')

                            global_var.level_settings.set_setting("combined",
                                                                  True)
                            global_var.level_settings.set_setting("fireball", False)
                            global_var.level_settings.set_setting("pipes", False)
                        else:
                            update_level_button_images(self.level_fireball_button, self.alpha_value, 'disabled')
                            update_level_button_images(self.level_pipe_button, self.alpha_value, 'enabled')
                            update_level_button_images(self.level_combine_button, self.alpha_value,
                                                       'disabled')
                            global_var.level_settings.set_setting("combined", False)
                            self.combined_button_state = 'disabled'


                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False
                    self.settings_changed()
                    self.start_menu()

            if global_var.settings_screen_state:
                self.settings.screen.fill((0, 0, 0))
                self.settings.screen.fill(pg.Color(78, 186, 196))
                self.settings.screen.blit(self.background.image, (0, 0))
                self.settings.screen.blit(settings_inner_rect, (0, 0))
                self.settings.screen.blit(self.base.image,
                                          (0, self.settings.game_screen_height - self.base.ground_bg.get_height()))
                self.settings.screen.blit(settings_title,
                                          (self.settings.game_screen_width // 2 - settings_title.get_width() // 2, 50))
                # Left half of settings screen: levels
                self.settings.screen.blit(banner_left, banner_left_rect)
                self.settings.screen.blit(levels_title, levels_rect)

                self.settings.screen.blit(self.pipe_level_surface, self.pipe_level_surface_rect)
                self.level_pipe_button.draw(self.settings.screen)
                self.settings.screen.blit(self.fireball_level_surface, self.fireball_level_surface_rect)
                self.level_fireball_button.draw(self.settings.screen)

                self.screen.blit(self.combine_level_surface, self.combine_level_surface_rect)
                self.level_combine_button.draw(self.screen)
                # Right half of settings screen: sound, language, input mode: keyboard and voice
                self.settings.screen.blit(item_name, item_rect)
                self.sound_button.draw(self.settings.screen)

                self.settings.screen.blit(lang_item_name, lang_item_rect)
                self.language_button.draw(self.settings.screen)

                self.settings.screen.blit(banner, banner_rect)
                self.settings.screen.blit(input_mode_title, input_mode_rect)

                self.settings.screen.blit(input_mode_keyboard_text, input_mode_keyboard_rect)
                self.keyboard_button.draw(self.settings.screen)

                self.settings.screen.blit(input_mode_voice_text, input_mode_voice_rect)
                self.voice_button.draw(self.settings.screen)

                pg.display.flip()
                pg.display.update()

    def settings_changed(self):
        if global_var.level_settings.get_setting('sound'):
            self.sound = True
        if global_var.level_settings.get_setting('pipes'):
            self.level_pipe = True
            self.level_fireball = False
            self.level_staircase = False
            self.level_combine = False
        elif global_var.level_settings.get_setting('fireball'):
            self.level_fireball = True
            self.level_pipe = False
            self.level_staircase = False
            self.level_combine = False
        elif global_var.level_settings.get_setting('staircase'):
            # self.rect.center = self.bird_images['start'].get_rect(center=(self.bird_x, self.bird_y))
            self.level_pipe = False
            self.level_fireball = False
            self.level_staircase = True
            self.level_combine = False
        elif global_var.level_settings.get_setting('combined'):
            self.level_pipe = False
            self.level_fireball = False
            self.level_staircase = False
            self.level_combine = True
        return self.sound, self.level_pipe, self.level_fireball, self.level_staircase, self.level_combine

    def create_level_layout(self, x, y, text):
        level_surface = pg.Surface((200, 50), pg.SRCALPHA)
        level_surface.fill((115, 147, 179, self.alpha_value + 30))
        level = self.settings.settings_options_font.render(text, True, (255, 255, 255))
        level_surface_rect = level_surface.get_rect(topleft=(x, y))

        return level_surface, level_surface_rect, level

    def start_menu(self):
        global_var.start_screen_state = True

        effective_screen_midpoint = self.effective_screen_height // 2
        welcome_x = self.settings.game_screen_width // 2 - self.welcome.get_width() // 2
        welcome_y = self.settings.game_screen_height // 2 - self.welcome.get_height() // 2 - effective_screen_midpoint // 2 - 30

        menu_height = effective_screen_midpoint - 50
        menu_width = self.welcome.get_width() - 200

        menu_x = (self.settings.game_screen_width - menu_width) // 2  # Center horizontally
        menu_y = self.settings.game_screen_height // 2 - menu_height // 2 + 100  # Center vertically

        menu_rect_alpha = pg.Surface((menu_width, menu_height), pg.SRCALPHA)

        # Set the transparency (alpha) level
        alpha_value = 150  # Adjust as needed, 0 = fully transparent, 255 = fully opaque
        menu_rect_alpha.fill((115, 147, 179, alpha_value))

        # Calculate positions of buttons relative to the menu_rect
        button_x = menu_x + menu_width // 2
        button_center_y = menu_y

        # Calculate vertical positions for each button
        button_height = self.images['button'].get_height()
        button_spacing = 10  # Adjust as needed for the vertical spacing between buttons

        # Calculate the starting y-position for the top button inside the menu_rect
        top_button_start_y = menu_height // 2 - (3.5 * button_height + button_spacing) // 2

        # Calculate the positions of the buttons relative to the menu_rect
        play_button_y = menu_y + top_button_start_y
        settings_button_y = play_button_y + button_height + button_spacing
        leaderboard_button_y = settings_button_y + button_height + button_spacing
        quit_button_y = leaderboard_button_y + button_height + button_spacing

        self.avatar = self.avatars[self.current_avatar]
        resized_avatar = pg.transform.scale(self.avatar, (50, 50))
        avatar_center_x = self.settings.game_screen_width - resized_avatar.get_width() // 2 - 70
        avatar_center_y = 20 + resized_avatar.get_height() // 2

        self.user_profile_button = Button(self.settings, self.constants, resized_avatar,
                                          avatar_center_x, avatar_center_y, '')

        # Place the buttons inside the menu_rect
        self.play_button = Button(self.settings, self.constants, self.images['button'], button_x, play_button_y, 'PLAY')
        self.settings_button = Button(self.settings, self.constants, self.images['button'], button_x, settings_button_y,
                                      'SETTINGS')
        self.leaderboard_button = Button(self.settings, self.constants, self.images['button'], button_x,
                                         leaderboard_button_y, 'LEADERBOARD')
        self.quit_button = Button(self.settings, self.constants, self.images['button'], button_x, quit_button_y, 'QUIT')

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()

                elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    if global_var.level_settings.get_setting('voice'):
                        if global_var.level_settings.get_setting('pipes'):
                            self.set_pipes_mode()

                        elif global_var.level_settings.get_setting('fireball'):
                            self.set_fireball_mode()

                        elif global_var.level_settings.get_setting('staircase'):
                            self.set_staircase_mode()

                    else:
                        global_var.start_screen_state = False
                        global_var.settings_screen_state = False
                        global_var.game_over_screen_state = False
                        global_var.leaderboard_screen_state = False


                    if global_var.level_settings.get_setting('keyboard'):
                        if global_var.level_settings.get_setting('pipes'):
                            self.set_pipes_mode()

                        elif global_var.level_settings.get_setting('fireball'):
                            self.set_fireball_mode()

                        elif global_var.level_settings.get_setting('staircase'):
                            self.set_staircase_mode()


                    global_var.start_screen_state = False
                    global_var.settings_screen_state = False
                    global_var.game_over_screen_state = False
                    global_var.leaderboard_screen_state = False
                    running = False
                    self.flying = True
                    self.game.run(self.bird)

                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.start_menu()

                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.play_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        if global_var.level_settings.get_setting('voice'):
                            if global_var.level_settings.get_setting('pipes'):
                                self.set_pipes_mode()

                            elif global_var.level_settings.get_setting('fireball'):
                                self.set_fireball_mode()

                            elif global_var.level_settings.get_setting('staircase'):
                                self.set_staircase_mode()

                        else:
                            global_var.start_screen_state = False
                            global_var.settings_screen_state = False
                            global_var.game_over_screen_state = False
                            global_var.leaderboard_screen_state = False

                        if global_var.level_settings.get_setting('keyboard'):
                            if global_var.level_settings.get_setting('pipes'):
                                self.set_pipes_mode()

                            elif global_var.level_settings.get_setting('fireball'):
                                self.set_fireball_mode()

                            elif global_var.level_settings.get_setting('staircase'):
                                self.set_staircase_mode()

                        global_var.start_screen_state = False
                        global_var.settings_screen_state = False
                        global_var.game_over_screen_state = False
                        global_var.leaderboard_screen_state = False
                        self.flying = True
                        running = False
                        self.game.run(self.bird)

                    if self.settings_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        running = False
                        global_var.start_screen_state = False
                        global_var.settings_screen_state = True
                        global_var.game_over_screen_state = False
                        global_var.leaderboard_screen_state = False
                        self.settings_screen()
                    if self.leaderboard_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        global_var.start_screen_state = False
                        global_var.settings_screen_state = False
                        global_var.game_over_screen_state = False
                        global_var.leaderboard_screen_state = True
                        self.leaderboard_screen()
                    if self.user_profile_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        self.set_user_profile()
                    if self.quit_button.check_for_mouse_input(pg.mouse.get_pos()):
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['click'].play()
                        pg.quit()
                        sys.exit()

            if global_var.start_screen_state:
                global_var.settings_screen_state = False
                global_var.game_over_screen_state = False
                global_var.leaderboard_screen_state = False
                # Calculate the oscillation for the bird using a sine function
                oscillate_bird = 20 * np.sin(0.005 * pg.time.get_ticks())

                # Clear the screen
                self.screen.fill((0, 0, 0))
                self.screen.blit(self.background.image, (0, 0))
                self.screen.blit(self.base.image,
                                 (0, self.settings.game_screen_height - self.base.ground_bg.get_height()))

                # Draw bird and welcome message with oscillation
                self.screen.blit(self.bird_image,
                                 (self.settings.game_screen_width // 2 - self.bird_image.get_width() // 2,
                                  50 + oscillate_bird))
                self.screen.blit(self.welcome, (welcome_x, welcome_y))

                self.avatar = self.avatars[self.current_avatar]
                resized_avatar = pg.transform.scale(self.avatar, (50, 50))
                avatar_center_x = self.settings.game_screen_width - resized_avatar.get_width() // 2 - 70
                avatar_center_y = 20 + resized_avatar.get_height() // 2

                self.user_profile_button = Button(self.settings, self.constants, resized_avatar,
                                                  avatar_center_x, avatar_center_y, '')

                self.user_profile_button.draw(self.screen)

                self.user_name = self.settings.menu_font.render(global_var.name, True, (0, 45, 98))

                text_width = self.user_name.get_width()
                text_x = avatar_center_x - (text_width // 2)
                text_y = avatar_center_y + resized_avatar.get_height() // 2 + 10  # Adjust as needed for spacing

                self.screen.blit(self.user_name, (text_x, text_y))

                self.screen.blit(menu_rect_alpha, (menu_x, menu_y))

                self.play_button.draw(self.screen)
                self.play_button.change_color(pg.mouse.get_pos())

                self.settings_button.draw(self.screen)
                self.settings_button.change_color(pg.mouse.get_pos())

                self.leaderboard_button.draw(self.screen)
                self.leaderboard_button.change_color(pg.mouse.get_pos())

                self.quit_button.draw(self.screen)
                self.quit_button.change_color(pg.mouse.get_pos())

            # Update the display
            pg.display.update()
            pg.display.flip()

    def leaderboard_screen(self):
        global_var.leaderboard_screen_state = True
        leaderboard_title = self.settings.title_font.render('Leader Board', True, (255, 255, 255))
        leaderboard_title_rect = leaderboard_title.get_rect()
        leaderboard_inner_rect_height = self.effective_screen_height - leaderboard_title_rect.height - 100
        leaderboard_inner_rect = pg.Surface((self.settings.game_screen_width - 200, leaderboard_inner_rect_height),
                                            pg.SRCALPHA)
        leaderboard_inner_rect.fill((102, 153, 204, self.alpha_value))
        leaderboard_inner_rect_rect = leaderboard_inner_rect.get_rect(topleft=(100, leaderboard_title_rect.height + 70))
        self.prepare_screen()
        self.screen.blit(leaderboard_title,
                         (self.settings.game_screen_width // 2 - leaderboard_title.get_width() // 2, 50))
        self.screen.blit(leaderboard_inner_rect, leaderboard_inner_rect_rect.topleft)
        y_offset = leaderboard_inner_rect_rect.top + 20
        row_height = 50
        leaderboard_data = load_leaderboard(self.settings)

        # Define desired row width (this can be dynamic if needed)
        row_width = leaderboard_inner_rect_rect.width - 700

        for i, data in enumerate(leaderboard_data):
            if y_offset + row_height > leaderboard_inner_rect_rect.bottom:
                break

            # Calculate x position to center the row inside the inner rect
            x_pos = leaderboard_inner_rect_rect.left + (leaderboard_inner_rect_rect.width - row_width) // 2

            row_color = (255, 255, 255) if i % 2 == 0 else (200, 200, 200)
            row = pg.draw.rect(self.screen, row_color, (x_pos, y_offset, row_width, row_height - 10))

            # Load and display avatar
            avatar = load_avatar(data['avatar'])
            if avatar:
                avatar = pg.transform.scale(avatar, (40, 40))
                self.screen.blit(avatar, (row.left + 50, y_offset))  # Display avatar

            # Display player name
            name_text = self.settings.menu_font.render(data['name'], True, (0, 0, 0))
            self.screen.blit(name_text, (row.left + 120, y_offset + 10))  # Name position

            # Display player score
            score_text = self.settings.menu_font.render(str(data['score']), True, (0, 0, 0))
            self.screen.blit(score_text, (row.left + 300, y_offset + 10))  # Score position

            y_offset += row_height

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False
                    self.start_menu()

            if global_var.leaderboard_screen_state:
                pg.display.update()
                pg.display.flip()

    def set_user_profile(self):
        text_input = TextInput(self.settings.menu_font, global_var.name)
        temp = True
        while temp:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and (event.key == pg.K_ESCAPE):
                    temp = False
                elif event.type == pg.KEYDOWN or event.type == pg.TEXTINPUT:
                    text_input.handle_event(event)
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.next_button.check_for_mouse_input(pg.mouse.get_pos()):
                        global_var.current_avatar = (global_var.current_avatar + 1) % len(self.avatars)
                    elif self.prev_button.check_for_mouse_input(pg.mouse.get_pos()):
                        global_var.current_avatar = (global_var.current_avatar - 1) % len(self.avatars)

            # Draw the background and avatar selection
            self.prepare_screen()
            avatar_image = self.avatars[global_var.current_avatar]
            avatar_image = pg.transform.scale(avatar_image, (256, 256))
            avatar_x = self.settings.game_screen_width // 2 - avatar_image.get_width() // 2
            avatar_y = int(self.settings.game_screen_height * 0.2)
            avatar_image_rect = avatar_image.get_rect(topleft=(avatar_x, avatar_y))
            avatar_center_y = avatar_y + avatar_image.get_height() // 2
            button_spacing = 50
            prev_button_x = avatar_image_rect.left - button_spacing
            prev_button_y = avatar_center_y
            next_button_x = avatar_image_rect.right + button_spacing
            next_button_y = avatar_center_y

            # Positioning for the "Enter Name" text
            text_surface = self.settings.menu_font.render('Enter Name:', True, (0, 0, 0))
            text_x = self.settings.game_screen_width // 2 - text_surface.get_width() // 2
            text_y = avatar_y + 256 + 20  # Place below the profile picture with a margin of 20 pixels
            self.screen.blit(text_surface, (text_x, text_y))

            # Positioning for the text box
            text_box_width = 200
            text_box_height = 50
            text_box_x = self.settings.game_screen_width // 2 - text_box_width // 2
            text_box_y = text_y + text_surface.get_height() + 10  # Place below the text with a margin of 10 pixels
            text_box_rect = pg.Rect(text_box_x, text_box_y, text_box_width, text_box_height)

            self.screen.blit(avatar_image, avatar_image_rect.topleft)
            self.next_button = Button(self.settings, self.constants, self.images['arrow_right'], next_button_x,
                                      next_button_y, '')
            self.prev_button = Button(self.settings, self.constants, self.images['arrow_left'], prev_button_x,
                                      prev_button_y, '')

            self.screen.blit(avatar_image, avatar_image_rect.topleft)
            self.next_button.draw(self.screen)
            self.next_button.change_color(pg.mouse.get_pos())
            self.prev_button.draw(self.screen)
            self.prev_button.change_color(pg.mouse.get_pos())

            text_input.draw(self.screen, text_box_rect)
            text_input.update()

            pg.display.update()
            global_var.name = text_input.text
            self.name = global_var.name
            self.current_avatar = global_var.current_avatar
            avatar_base_path = "../assets/images/avatars"
            avatar_path = f"{avatar_base_path}/{self.current_avatar + 1}.png"
            global_var.level_settings.set_setting("player_name", self.name)
            global_var.level_settings.set_setting("avatar_path", avatar_path)

        return self.name, self.avatars[self.current_avatar]

    def show_game_over_screen(self, score, star_ring_1, star_ring_2, background, pipes, bird, base, fireball, particles,
                              delta_time, screen):
        # Display game over screen
        if global_var.game_over and global_var.game_over_screen_state:
            self.score_manager.update_score(score)
            save_to_csv(self.settings.json_file_path, self.settings.csv_file_path)
            global_var.level_settings.set_setting('score', score)

            running = True
            while running:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            running = False
                            self.game.restart()
                            self.start_menu()
                        if event.key == pg.K_SPACE:
                            running = False
                            self.game.restart()
                            self.game.run(self.bird)

                if global_var.level_settings.get_setting('pipes'):
                    background.update()
                    bird.update(delta_time, False, False)
                    star_ring_1.update()
                    star_ring_2.update()

                    background.draw(screen)
                    pipes.draw(screen)
                    base.draw(screen)

                    overlay_color = (115, 147, 179, 150)  # Change this to your desired color and transparency level
                    overlay_surface = pg.Surface((self.settings.game_screen_width, self.settings.game_screen_height),
                                                 pg.SRCALPHA)
                    overlay_surface.fill(overlay_color)
                    screen.blit(overlay_surface, (0, 0))

                    bird.draw(screen)
                    star_ring_1.draw(screen)
                    star_ring_2.draw(screen)

                if global_var.level_settings.get_setting('fireball'):
                    background.update()
                    fireball.update(self.effective_screen_height)
                    particles.update()
                    bird.update(delta_time, False, False)
                    star_ring_1.update()
                    star_ring_2.update()

                    background.draw(screen)
                    fireball.draw(screen)
                    particles.draw(screen)
                    base.draw(screen)

                    overlay_color = (115, 147, 179, 150)  # Change this to your desired color and transparency level
                    overlay_surface = pg.Surface((self.settings.game_screen_width, self.settings.game_screen_height),
                                                 pg.SRCALPHA)
                    overlay_surface.fill(overlay_color)
                    screen.blit(overlay_surface, (0, 0))

                    bird.draw(screen)
                    star_ring_1.draw(screen)
                    star_ring_2.draw(screen)

                screen.blit(self.images['game_over'],
                            (self.settings.game_screen_width // 2 - self.images['game_over'].get_width() // 2,
                             self.settings.game_screen_height // 2 - self.images['game_over'].get_height() // 2))
                show_score(self.settings, score)

                # Update the display
                pg.display.update()
                pg.display.flip()


    def prepare_screen(self):
        self.screen.fill((0, 0, 0))
        self.settings.screen.fill(pg.Color(78, 186, 196))
        self.settings.screen.blit(self.background.image, (0, 0))
        calibrate_inner_rect = pg.Surface((self.settings.game_screen_width, self.settings.game_screen_height),
                                          pg.SRCALPHA)
        calibrate_inner_rect.fill((102, 153, 204, self.alpha_value))

        self.settings.screen.blit(calibrate_inner_rect, (0, 0))
        self.settings.screen.blit(self.base.image,
                                  (0, self.settings.game_screen_height - self.base.ground_bg.get_height()))

    def set_pipes_mode(self):
        bird_image = self.images['bird']
        self.bird = Bird(self.settings, self.constants, self.bird_sprites, bird_image,
                         self.base, self.sounds, self.constants.bird_start_x, self.constants.bird_start_y)

    def set_staircase_mode(self):
        bird_run_image = self.images['bird_staircase']
        bird_start_x = 200
        bird_offset = self.bird_stairs.image.get_rect().height
        bird_start_y = self.base.rect.top - (self.bird_stairs.image.get_rect().height // 2)
        self.bird = BirdWalk(self.settings, self.constants, self.bird_stairs_sprites, bird_run_image,
                             self.base, self.sounds, bird_start_x, bird_start_y)

    def set_fireball_mode(self):
        bird_ak_image = self.images['bird_ak']
        self.bird = Bird(self.settings, self.constants, self.bird_sprites, bird_ak_image,
                         self.base, self.sounds, self.constants.bird_fireball_start_x,
                         self.constants.bird_fireball_start_y)

    def get_bird(self):
        return self.bird