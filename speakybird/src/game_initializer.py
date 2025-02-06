import pygame as pg
import pygame.mixer as mixer
import threading

import global_var
from asset_manager import ImageManager, SoundManager
from transcriber_faster_whisper import FasterWhisperTranscriber
from player_profile_manager import ScoreManager, LevelSettings
from sprites import BG, BaseImage
from whisper_transcriber import WhisperTranscriber


class GameInitializer:
    def __init__(self, settings, constants):
        mixer.pre_init(frequency=44100, size=16, channels=1, buffer=512)
        # pg.init()
        self.settings = settings
        self.constants = constants
        global_var.level_settings = LevelSettings(self.settings.json_file_path)
        global_var.level_settings.reset_to_defaults()
        self.screen = self.settings.screen
        pg.display.set_caption(self.settings.title)
        self.clock = pg.time.Clock()

        self.parser = None

        self.running = False
        self.flying = self.settings.flying

        # sprite groups
        self.background_sprites = pg.sprite.Group()
        self.ground_sprites = pg.sprite.Group()
        self.bird_sprites = pg.sprite.Group()
        self.bird_stairs_sprites = pg.sprite.Group()
        self.pipe_sprites = pg.sprite.Group()

        self.stairs_sprites = pg.sprite.Group()

        self.fireball_sprites = pg.sprite.Group()

        self.phrases_sprites = pg.sprite.Group()
        self.positive_sprites = pg.sprite.Group()
        self.negative_sprites = pg.sprite.Group()
        self.bullets_sprites = pg.sprite.Group()

        self.star_ring_sprites = pg.sprite.Group()
        self.particle_sprites = pg.sprite.Group()

        # star ring
        self.star_ring_1 = None
        self.star_ring_2 = None

        # sound
        self.sound = SoundManager(self.settings, self.constants)
        self.sounds = self.sound.sound_loader()

        # image manager
        self.image_manager = ImageManager(self.settings, self.constants)
        self.images = self.image_manager.image_loader()

        # create avatar
        self.avatars = []
        self.avatars = self.images['avatars']

        # create background
        self.bg_image = self.images['background']
        self.background = BG(self.background_sprites, self.bg_image, self.settings)

        # create base
        self.base_image = self.images['ground']
        self.base = BaseImage(self.settings, self.constants, self.ground_sprites, self.base_image,
                              0, (self.screen.get_height() - self.base_image.get_height()))

        # create bird image
        self.bird_image = self.images['bird']
        self.bird_ak_image = self.images['bird_ak']

        self.bird_stair_image = self.images['bird_staircase']

        # create pipe
        self.last_pipe = pg.time.get_ticks() - self.constants.pipe_frequency
        self.pipe_upper = self.images['pipe_upper']
        self.pipe_lower = self.images['pipe_lower']

        self.effective_screen_height = self.screen.get_height() - self.base_image.get_height()

        # fireball
        self.fireball_images = self.images['fireball']
        self.last_fireball = 0

        self.bullet_image = self.images['bullet']

        self.last_phrase_time = 0

        # audio
        self.transcriber = None
        # score
        self.score_manager = ScoreManager(self.settings.json_file_path, self.sounds)

        # buttons
        self.play_button = None
        self.settings_button = None
        self.leaderboard_button = None
        self.quit_button = None

        self.maybe_jump = False

        self.hit_sound = False

        self.shared_data = {
            'record_start_time': None,
            'record_end_time': None,
            'record_mid_time': None,
            'transcribe_start_time': None,
            'transcribe_end_time': None,
            'jump_end_time': None,
            'command_check_time': None,
            'data': None,
            'lock': threading.Lock()
        }

    def set_speech_recognition_model(self, model, plot_transcribe_time):
        if model == 'faster_whisper':
            print("Using faster-whisper model")
            self.transcriber = FasterWhisperTranscriber(self.constants, plot_transcribe_time, self.shared_data)
            self.parser = self.transcriber.get_parser()
            assert(self.parser is not None)
        else:
            print("Using whisper model")
            self.transcriber = WhisperTranscriber(self.settings, self.constants, plot_transcribe_time)
