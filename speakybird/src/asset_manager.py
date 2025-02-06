import glob
import random

import pygame as pg


class ImageManager:
    def __init__(self, settings, constants):
        self.settings = settings
        self.constants = constants
        self.screen_width = self.settings.game_screen_width
        self.screen_height = self.settings.game_screen_height
        self.images = {}
        self.image_loader()

        self.rand_bg = None
        self.rand_bird = None
        self.rand_pipe = None

    def image_loader(self):
        # Load the images
        self.images['background'] = (
            pg.image.load('../assets/images/sprites/background-day.png').convert(),
            pg.image.load('../assets/images/sprites/background-night.png').convert()
        )
        self.images['ground'] = pg.image.load('../assets/images/sprites/base.png').convert()

        # Bird images
        self.images['bird_color'] = tuple(
            (f'../assets/images/sprites/{color}bird-upflap.png',
             f'../assets/images/sprites/{color}bird-midflap.png',
             f'../assets/images/sprites/{color}bird-downflap.png')
            for color in ['red', 'blue', 'yellow']
        )

        # Set upper pipe images based on the chosen color

        self.images['game_over'] = pg.image.load('../assets/images/sprites/gameover.png').convert_alpha()
        self.images['restart'] = pg.image.load('../assets/images/sprites/restart.png').convert_alpha()
        self.randomizer()

        self.images['pipe_upper'] = pg.image.load(
            f'../assets/images/sprites/pipe-{self.rand_pipe}-upper.png').convert_alpha()
        self.images['pipe_upper'] = pg.transform.smoothscale(self.images['pipe_upper'], (
            self.images['pipe_upper'].get_width(),
            self.screen_height - self.images['ground'].get_height() - self.constants.pipe_gap))

        self.images['pipe_lower'] = pg.image.load(f'../assets/images/sprites/pipe-{self.rand_pipe}.png').convert_alpha()
        self.images['pipe_lower'] = pg.transform.smoothscale(self.images['pipe_lower'], (
            self.images['pipe_lower'].get_width(),
            self.screen_height - self.images['ground'].get_height() - self.constants.pipe_gap))

        self.images['background'] = self.images['background'][self.rand_bg]

        self.images['bird'] = (
            pg.image.load(self.images['bird_color'][self.rand_bird][0]).convert_alpha(),
            pg.image.load(self.images['bird_color'][self.rand_bird][1]).convert_alpha(),
            pg.image.load(self.images['bird_color'][self.rand_bird][2]).convert_alpha(),
        )

        self.images['bird_ak'] = tuple(
            (pg.image.load('../assets/images/sprites/Ak_upflap.png').convert_alpha(),
             pg.image.load('../assets/images/sprites/Ak_midflap.png').convert_alpha(),
             pg.image.load('../assets/images/sprites/Ak_downflap.png').convert_alpha())
        )
        self.images['bird_ak'] = (
            pg.transform.scale(self.images['bird_ak'][0], (
                self.images['bird_ak'][0].get_width() + 10, self.images['bird_ak'][0].get_height() + 5)),
            pg.transform.scale(self.images['bird_ak'][1], (
                self.images['bird_ak'][1].get_width() + 10, self.images['bird_ak'][1].get_height() + 5)),
            pg.transform.scale(self.images['bird_ak'][2], (
                self.images['bird_ak'][2].get_width() + 10, self.images['bird_ak'][2].get_height() + 5))
        )

        self.images['bird_staircase'] = {
            'start': pg.image.load('../assets/images/sprites/midflap_start.png').convert_alpha(),
            'run': [
                pg.image.load('../assets/images/sprites/midflap_run1.png').convert_alpha(),
                pg.image.load('../assets/images/sprites/midflap_run2.png').convert_alpha()
            ],
            'jump': pg.image.load('../assets/images/sprites/midflap_start.png').convert_alpha()
        }
        self.images['bird_staircase'] = {
            'start': pg.transform.scale_by(self.images['bird_staircase']['start'], 1.3),
            'run': [
                pg.transform.scale_by(self.images['bird_staircase']['run'][0], 1.3),
                pg.transform.scale_by(self.images['bird_staircase']['run'][1], 1.3),
            ],
            'jump': pg.transform.scale_by(self.images['bird_staircase']['start'], 1.3),
        }

        self.images['staircase'] = pg.image.load('../assets/images/sprites/stair_no_top.png').convert_alpha()

        self.images['smoke'] = pg.image.load('../assets/images/sprites/smoke/Smoke_2_128.png')

        self.images['welcome'] = pg.image.load('../assets/images/sprites/speaky_bird.png').convert_alpha()

        self.images['button'] = pg.image.load('../assets/images/sprites/button_white.png').convert_alpha()
        self.images['button'] = pg.transform.scale(self.images['button'], (200, 50))

        self.images['arrow_right'] = pg.image.load('../assets/images/sprites/right_arrow_yellow.png').convert_alpha()
        self.images['arrow_right'] = pg.transform.scale(self.images['arrow_right'], (50, 50))
        self.images['arrow_left'] = pg.transform.flip(self.images['arrow_right'], True, False)

        self.images['toggle_on'] = pg.image.load('../assets/images/sprites/toggle_on.png').convert_alpha()
        self.images['toggle_on'] = pg.transform.scale(self.images['toggle_on'], (50, 25))
        self.images['toggle_off'] = pg.image.load('../assets/images/sprites/toggle_off.png').convert_alpha()
        self.images['toggle_off'] = pg.transform.scale(self.images['toggle_off'], (50, 25))

        self.images['english'] = pg.image.load('../assets/images/sprites/english.png').convert_alpha()
        self.images['english'] = pg.transform.scale(self.images['english'], (50, 25))
        self.images['german'] = pg.image.load('../assets/images/sprites/german.png').convert_alpha()
        self.images['german'] = pg.transform.scale(self.images['german'], (50, 25))

        avatar_paths = sorted(glob.glob('../assets/images/avatars/*.png'))  # Adjust path as necessary
        self.images['avatars'] = [pg.image.load(path).convert_alpha() for path in avatar_paths]

        fireball_paths = sorted(glob.glob('../assets/images/sprites/fireball/*.png'))
        self.images['fireball'] = [pg.image.load(path).convert_alpha() for path in fireball_paths]
        self.images['fireball'] = [pg.transform.scale(img, (self.constants.fireball_width,
                                                            self.constants.fireball_height)) for img in
                                   self.images['fireball']]
        self.images['fireball'] = [pg.transform.flip(img, True, False) for img in self.images['fireball']]

        self.images['bullet'] = pg.image.load('../assets/images/sprites/bullet.png')
        self.images['bullet'] = pg.transform.scale(self.images['bullet'], (15, 15))

        return self.images

    def randomizer(self):
        self.rand_bg = random.randint(0, len(self.images['background']) - 1)
        self.rand_bird = random.randint(0, len(self.images['bird_color']) - 1)
        self.rand_pipe = random.choice(['green', 'red'])



class SoundManager:
    def __init__(self, settings, constants):
        self.settings = settings
        self.constants = constants
        self.sounds = {}

    def sound_loader(self):
        self.sounds['wing'] = pg.mixer.Sound('../assets/sounds/wing.wav')
        self.sounds['hit'] = pg.mixer.Sound('../assets/sounds/hit.wav')
        self.sounds['point'] = pg.mixer.Sound('../assets/sounds/coin_collect.wav')
        self.sounds['die'] = pg.mixer.Sound('../assets/sounds/die.wav')
        self.sounds['balloon_pop'] = pg.mixer.Sound('../assets/sounds/balloon-pop.wav')
        self.sounds['wrong'] = pg.mixer.Sound('../assets/sounds/wrong.wav')
        self.sounds['fire_burn'] = pg.mixer.Sound('../assets/sounds/fire-burn.wav')
        self.sounds['click'] = pg.mixer.Sound('../assets/sounds/click-menu.wav')
        self.sounds['stairjump']=pg.mixer.Sound('../assets/sounds/stair_jump.wav')
        self.sounds['running'] = pg.mixer.Sound('../assets/sounds/run.wav')
        # self.sounds['swoosh'] = pg.mixer.Sound('../assets/sounds/swoosh.wav')
        for sound in self.sounds.values():
            sound.set_volume(0.2)


        return self.sounds
