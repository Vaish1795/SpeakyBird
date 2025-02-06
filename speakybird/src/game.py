import time

from game_initializer import GameInitializer
from sprites import *
from supporter import render_message


class Game(GameInitializer):
    def __init__(self, model, plot_transcribe_time, transcriber, screens, settings, constants, shared_data):
        super().__init__(settings, constants)
        self.model = model
        self.plot_transcribe_time = plot_transcribe_time
        self.transcriber = transcriber
        self.screens = screens
        self.bird = None
        self.parser = transcriber.get_parser()
        self.stairs = None
        self.start_time = 0

        self.is_voice = False
        self.is_pipes = False
        self.is_fireball = False

        self.is_staircase = False
        self.is_combined = False

        self.is_sound = False

        self.word_disp = False
        self.color_change_duration = 0.5
        self.last_command_time = time.time()
        self.color = 'WHITE'

        self.cool_down_period = 1

        self.shared_data = shared_data
        self.score_before_fireball = 0

        self.stop_spawning = False

    def restart(self):
        # Reset relevant game variables
        global_var.game_over = False
        global_var.game_over_screen_state = False
        global_var.prompt_calibrate_state = False
        global_var.calibrate_screen_state = False
        global_var.start_screen_state = False
        global_var.settings_screen_state = False
        global_var.game_over_screen_state = False
        global_var.leaderboard_screen_state = False

        global_var.flying = False
        global_var.game_over = False

        global_var.moving_up = False
        global_var.moving_down = False

        global_var.render_message = False

        global_var.stairs = []
        global_var.stairs_rect = []
        global_var.stop_position = 0

        self.flying = False
        self.hit_sound = False

        # Clear sprite groups
        self.background_sprites.empty()
        self.ground_sprites.empty()
        self.bird_sprites.empty()
        self.bird_stairs_sprites.empty()
        self.pipe_sprites.empty()
        self.phrases_sprites.empty()
        self.positive_sprites.empty()
        self.negative_sprites.empty()
        self.bullets_sprites.empty()
        self.particle_sprites.empty()
        self.fireball_sprites.empty()
        self.stairs_sprites.empty()

        # Reset last pipe time
        self.last_pipe = pg.time.get_ticks() - self.constants.pipe_frequency

        # Recreate initial game elements
        self.background = BG(self.background_sprites, self.bg_image, self.settings)
        self.base = BaseImage(self.settings, self.constants, self.ground_sprites, self.base_image,
                              0, (self.screen.get_height() - self.base_image.get_height()))
        # self.bird = Bird(self.settings, self.constants, self.bird_sprites, self.bird_image, self.base, self.sounds)
        self.score_manager.reset_score()
        self.stop_spawning = False

        if self.is_combined:
            global_var.level_settings.set_setting("pipes", False)
            global_var.level_settings.set_setting("fireball", False)
            global_var.level_settings.set_setting("staircase", False)
            global_var.level_settings.set_setting("combined", True)

        if global_var.level_settings.get_setting('voice'):
            self.set_speech_recognition_model(self.model, self.plot_transcribe_time)
        self.screens.start_menu()

        self.score_before_fireball = 0

    def set_settings_variables(self):
        self.is_voice = global_var.level_settings.get_setting('voice')
        self.is_pipes = global_var.level_settings.get_setting('pipes')
        self.is_fireball = global_var.level_settings.get_setting('fireball')
        self.is_staircase = global_var.level_settings.get_setting('staircase')
        self.is_combined = global_var.level_settings.get_setting('combined')

        if self.is_combined:
            # global_var.level_settings.set_setting("combined", True)
            self.set_pipes_mode()
            self.reset()

        self.is_sound = global_var.level_settings.get_setting('sound')

    def set_pipes_mode(self):
        self.is_pipes = True
        self.is_staircase = False
        self.is_fireball = False
        global_var.level_settings.set_setting("pipes", True)
        global_var.level_settings.set_setting("fireball", False)
        global_var.level_settings.set_setting("staircase", False)
        global_var.level_settings.set_setting("combined", True)
        self.screens.set_pipes_mode()

    def set_staircase_mode(self):
        self.is_pipes = False
        self.is_staircase = True
        self.is_fireball = False
        global_var.level_settings.set_setting("pipes", False)
        global_var.level_settings.set_setting("fireball", False)
        global_var.level_settings.set_setting("staircase", True)
        global_var.level_settings.set_setting("combined", True)
        self.screens.set_staircase_mode()

    def set_fireball_mode(self):
        self.is_pipes = False
        self.is_staircase = False
        self.is_fireball = True
        global_var.level_settings.set_setting("pipes", False)
        global_var.level_settings.set_setting("fireball", True)
        global_var.level_settings.set_setting("staircase", False)
        global_var.level_settings.set_setting("combined", True)
        self.screens.set_fireball_mode()

    def reset(self):
        self.bird = self.screens.get_bird()
        self.bird_sprites.empty()
        self.bird_sprites.add(self.bird)
        self.draw()
        self.parser.update_words()
        self.transcriber.set_level_settings()
        self.transcriber.clear_transcribe_result()

    def render_instructions(self):
        global_var.render_message = True
        self.screens.prepare_screen()
        if self.is_pipes:
            message = (
                "Navigate the bird through the pipes by saying the command displayed on the screen. " 
                "If you hit a pipe or the ground, the game is over."
            )
            render_message(self.settings, message)
            time.sleep(7)
        elif self.is_fireball and not self.is_combined:
            message = (
                "Shoot the negative statements by saying the command displayed. "
                "To move up and down, use the up and down arrow keys. "
                "If you get hit by a fireball, the game is over. "
            )
            render_message(self.settings, message)
            time.sleep(7)
            global_var.render_message = False
            global_var.render_message = True
            self.screens.prepare_screen()
            message = (
                "If you shoot a positive statement, you will lose a point. "
            )
            render_message(self.settings, message)
            time.sleep(4)
        global_var.render_message = False


    def run(self, bird):
        self.bird = bird
        self.bird_sprites.add(self.bird)
        last_time = time.time()
        self.set_settings_variables()
        if self.is_voice:
            self.transcriber.start_recording()
        # if self.is_staircase:
        number_stairs = len(global_var.command_stairs)
        self.stairs = Staircase(self.stairs_sprites, self.settings, self.images['staircase'], self.base_image, number_stairs)

        self.running = True
        self.screens.settings_changed()
        self.render_instructions()

        counter = 0
        while self.running:
            self.maybe_jump = False
            if not global_var.game_over:
                self.clock.tick(self.settings.frame_rate)
                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time
                # Main game loop or relevant section
                if self.is_pipes:
                    # Check if the player has reached the score threshold to stop spawning pipes
                    if self.is_combined and self.score_manager.get_score() == self.constants.max_pipes_score:
                        self.stop_spawning = True  # Stop spawning any new pipes

                    # Spawn pipes only if spawning is allowed
                    if not self.stop_spawning and (current_time - self.last_pipe > self.constants.pipe_frequency):
                        if self.bird.bird_alive and self.flying:
                            spawn_pipes(
                                self.images, self.settings, self.constants,
                                self.effective_screen_height, self.pipe_sprites
                            )
                            self.last_pipe = current_time

                    # Check if all pipes have left the screen to transition to staircase mode
                    pipes_off_screen = all(
                        pipe.rect.right < 0 for pipe in self.pipe_sprites)  # Check if pipes are off the screen
                    if self.stop_spawning and pipes_off_screen:
                        self.screens.prepare_screen()
                        global_var.render_message = True
                        message = (
                            "You are doing great! Now let's move to the next level. "
                            "In this level, say the statements displayed to jump the stairs."
                        )
                        render_message(self.settings, message)
                        time.sleep(5)
                        global_var.render_message = False
                        self.set_staircase_mode()
                        self.reset()
                        continue

                    # Check for collisions with pipes or ground
                    collision_pipes = pg.sprite.groupcollide(
                        self.bird_sprites, self.pipe_sprites, False, False, collided=pg.sprite.collide_mask
                    )
                    collision_ground = pg.sprite.groupcollide(
                        self.bird_sprites, self.ground_sprites, False, False, collided=pg.sprite.collide_mask
                    )

                    if collision_ground or collision_pipes:
                        self.bird.bird_alive = False
                        global_var.game_over = True
                        self.transcriber.stop_recording()
                        if global_var.level_settings.get_setting('sound') and not self.hit_sound:
                            self.sounds['hit'].play()
                            self.sounds['die'].play()
                            self.hit_sound = True

                    # Handle voice-based jump trigger
                    is_jump = self.transcriber.output()
                    if self.is_voice and is_jump:
                        current_time = time.time()
                        if current_time - self.last_command_time > self.cool_down_period:
                            self.color = self.constants.recognized_color
                            self.last_command_time = current_time
                            self.maybe_jump = True
                            self.bird.jump(self.maybe_jump)
                        self.transcriber.clear_transcribe_result()

                    # Process events, update game state, and render
                    self.events()
                    self.update(delta_time, self.maybe_jump, self.flying)
                    self.draw()

                    if global_var.game_over:
                        self.call_game_over_screen(delta_time)

                if self.is_fireball:
                    if current_time - self.last_phrase_time > self.constants.last_phrase_interval and len(
                            self.phrases_sprites) < 3 and self.flying:
                        self.last_phrase_time = current_time
                        spawn_phrase(self.settings, self.constants, self.effective_screen_height, self.phrases_sprites,
                                     self.positive_sprites, self.negative_sprites)
                    if current_time - self.last_fireball > self.constants.last_fireball_interval and self.flying:
                        spawn_fireball(self.fireball_images, self.settings, self.constants, self.screen,
                                       self.fireball_sprites, self.bird_sprites, self.sounds)
                        self.last_fireball = current_time

                    collision_fireball = pg.sprite.groupcollide(self.fireball_sprites, self.bird_sprites, False, False,
                                                             collided=pg.sprite.collide_mask)
                    if collision_fireball:
                        self.bird.bird_alive = False
                        global_var.game_over = True
                        if global_var.level_settings.get_setting('sound'):
                            self.sounds['hit'].play()
                            self.sounds['fire_burn'].play()
                        self.transcriber.stop_recording()
                        self.call_game_over_screen(delta_time)

                    is_shoot = self.transcriber.output()
                    if self.is_voice and is_shoot:
                        current_time = time.time()
                        if current_time - self.last_command_time > self.cool_down_period:
                            self.color = self.constants.recognized_color
                            self.last_command_time = current_time
                            shoot(self.bird, self.bullets_sprites, self.bullet_image, self.settings,
                                  self.phrases_sprites, self.positive_sprites, self.negative_sprites, self.sounds,
                                  self.particle_sprites)
                        self.transcriber.clear_transcribe_result()

                    self.events()
                    self.update(delta_time, self.maybe_jump, self.flying)
                    self.draw()


                    if self.score_manager.get_score() == self.score_before_fireball + self.constants.max_fireballs_score:
                        rendering_message = True
                        self.transcriber.stop_recording()
                        if self.is_combined:
                            self.screens.prepare_screen()
                            global_var.render_message = True
                            message = "Congratulations! You've successfully completed all the levels. To go back to the main menu, press the escape key."
                            render_message(self.settings, message)
                            while rendering_message:
                                for event in pg.event.get():
                                    if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                                        rendering_message = False
                                        self.running = False
                                        self.restart()
                                        self.screens.start_menu()
                        # time.sleep(5)
                        # global_var.render_message = False
                        global_var.game_over = True
                        self.call_game_over_screen(delta_time)

                if self.is_staircase:
                    is_statement = self.transcriber.output()
                    if self.is_voice and is_statement and counter < len(global_var.command_stairs):
                        counter += 1
                        current_time = time.time()
                        if current_time - self.last_command_time > self.cool_down_period:
                            self.color = self.constants.recognized_color
                            self.last_command_time = current_time
                        self.bird.is_moving = True
                        self.bird.jump_to_next_stair = True
                    if self.bird.stair_jump_complete():
                        self.parser.set_sentence()

                    self.events()
                    self.update(delta_time, self.maybe_jump, self.flying)
                    self.draw()

                    if self.bird.rect.right >= self.screen.get_width():
                        self.bird.rect.right = self.screen.get_width()
                        global_var.render_message = True
                        self.screens.prepare_screen()
                        message = "Amazing! You've reached the top of the stairs. Now let's fly to the next level."
                        render_message(self.settings, message)
                        time.sleep(3)
                        global_var.render_message = False
                        global_var.render_message = True
                        self.screens.prepare_screen()
                        message = "In this level, you need to shoot the negative statements by saying the command displayed. To move up and down, use the up and down arrow keys."
                        render_message(self.settings, message)
                        time.sleep(5)
                        global_var.render_message = False
                        self.set_fireball_mode()
                        self.reset()

                    self.score_before_fireball = self.score_manager.get_score()

    def call_game_over_screen(self, delta_time):
        global_var.game_over_screen_state = True
        self.running = False
        self.star_ring_1 = StarRing((self.bird.rect.centerx, self.bird.rect.top), 3, 30, 5, 30,
                                    0.5, 0)
        self.star_ring_2 = StarRing((self.bird.rect.centerx, self.bird.rect.top), 4, 50, 7, 65,
                                    0.7, 10)
        self.screens.show_game_over_screen(self.score_manager.get_score(), self.star_ring_1,
                                           self.star_ring_2, self.background_sprites, self.pipe_sprites,
                                           self.bird_sprites, self.ground_sprites,
                                           self.fireball_sprites, self.particle_sprites, delta_time,
                                           self.screen)

    def draw(self):
        self.background_sprites.draw(self.screen)
        if self.is_pipes:
            self.pipe_sprites.draw(self.screen)
            self.ground_sprites.draw(self.screen)
            self.bird_sprites.draw(self.screen)
        if self.is_fireball:
            self.phrases_sprites.draw(self.screen)
            self.fireball_sprites.draw(self.screen)
            self.ground_sprites.draw(self.screen)
            self.bird_sprites.draw(self.screen)
            self.bullets_sprites.draw(self.screen)
            self.particle_sprites.draw(self.screen)
        if self.is_staircase:
            self.ground_sprites.draw(self.screen)
            self.bird_sprites.draw(self.screen)
            self.stairs_sprites.draw(self.screen)

    def events(self):
        if self.is_pipes:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    if not global_var.game_over:
                        self.running = False
                        # self.flying = False
                        self.transcriber.clear_transcribe_result()
                        self.transcriber.stop_recording()
                        self.restart()
                        self.screens.start_menu()
                    if global_var.game_over:
                        self.restart()
                        self.screens.start_menu()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        if not self.flying:
                            self.flying = True
                        if global_var.game_over:
                            self.restart()
                        else:
                            self.maybe_jump = True
                            self.bird.jump(self.maybe_jump)

        if self.is_fireball:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    self.running = False
                    self.transcriber.clear_transcribe_result()
                    self.transcriber.stop_recording()
                    self.restart()
                    self.screens.start_menu()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        global_var.moving_up = True
                    elif event.key == pg.K_DOWN:
                        global_var.moving_down = True
                    if event.key == pg.K_SPACE:
                        if not self.flying:
                            self.flying = True
                        if global_var.game_over:
                            self.restart()
                        else:
                            shoot(self.bird, self.bullets_sprites, self.bullet_image, self.settings,
                                  self.phrases_sprites, self.positive_sprites, self.negative_sprites, self.sounds,
                                  self.particle_sprites)
                elif event.type == pg.KEYUP:
                    if event.key == pg.K_UP:
                        global_var.moving_up = False
                    elif event.key == pg.K_DOWN:
                        global_var.moving_down = False
            self.bird.movement(global_var.moving_up, global_var.moving_down, self.effective_screen_height)

        if self.is_staircase:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    if not global_var.game_over:
                        self.running = False
                        self.bird.is_moving = False
                        # self.flying = False
                        self.transcriber.clear_transcribe_result()
                        self.transcriber.stop_recording()
                        self.restart()
                        self.screens.start_menu()
                    if global_var.game_over:
                        self.restart()
                        self.screens.start_menu()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RIGHT:
                        self.bird.is_moving = True
                        if self.bird.rect.right >= self.screen.get_width():
                            self.bird.rect.right = self.screen.get_width()
                            self.bird.is_moving = False
                    if event.key == pg.K_SPACE:
                        self.bird.jump_to_next_stair = True

                        # # Record the time at which staircase level was completed.
                        # if self.staircase_complete_time is None and self.bird.all_stairs_jumped():
                        #     self.staircase_complete_time = time.time()
                        #
                        # # Switch to fireball mode 2 seconds after staircase mode was completed.
                        # if self.staircase_complete_time is not None and time.time() - self.staircase_complete_time > 2:
                        #     self.staircase_complete_time = None
                        #     self.set_fireball_mode()
                        #     self.reset()

    def update(self, delta_time, maybe_jump, is_flying):
        self.background_sprites.update(delta_time)
        if self.is_pipes:
            if self.bird.bird_alive and is_flying:
                self.pipe_sprites.update(delta_time, self.score_manager)
                self.ground_sprites.update(delta_time)
            self.bird_sprites.update(delta_time, maybe_jump, is_flying)
            if time.time() - self.last_command_time > self.color_change_duration:
                self.color = self.constants.not_recognized_color
            display_word(self.settings, global_var.command_pipe,
                         self.color)
        if self.is_fireball:
            if self.bird.bird_alive and is_flying:
                self.phrases_sprites.update(delta_time)
                self.fireball_sprites.update(self.effective_screen_height)
                self.ground_sprites.update(delta_time)
            self.bird_sprites.update(delta_time, maybe_jump, is_flying)
            self.bullets_sprites.update(self.score_manager)
            self.particle_sprites.update()
            if time.time() - self.last_command_time > self.color_change_duration:
                self.color = self.constants.not_recognized_color
            display_word(self.settings, global_var.command_fireball,
                         self.color)
        if self.is_staircase:
            self.bird_sprites.update(self.score_manager)
            self.stairs_sprites.update(self.screen)
            if time.time() - self.last_command_time > self.color_change_duration:
                self.color = self.constants.not_recognized_color
            display_word(self.settings, self.parser.get_sentence(),
                     self.color)

        show_score(self.settings, self.score_manager.get_score())

        pg.display.update()
        pg.display.flip()
