import pygame as pg


class Settings:
    def __init__(self):
        self.width = 1400
        self.height = 800
        # self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.screen = pg.display.set_mode((self.width, self.height))
        self.game_screen_width = pg.display.Info().current_w
        self.game_screen_height = pg.display.Info().current_h
        self.frame_rate = 60
        self.title = 'Wings of Positivity'
        self.window = pg.Rect(0, 0, self.game_screen_width, self.game_screen_height)

        self.font = pg.font.Font('../assets/fonts/fff-forward.regular.ttf', 40)
        self.menu_font = pg.font.Font('../assets/fonts/PixeloidMono-d94EV.ttf', 20)
        self.title_font = pg.font.Font('../assets/fonts/fff_forward.ttf', 40)
        self.subtitle_font = pg.font.Font('../assets/fonts/fff-forward.regular.ttf', 20)
        self.settings_options_font = pg.font.Font('../assets/fonts/PixeloidMono-d94EV.ttf', 30)

        self.command_font = pg.font.Font('../assets/fonts/PixeloidMono-d94EV.ttf', 50)

        self.calibration_font = pg.font.Font('../assets/fonts/Retro_Gaming.ttf', 40)
        self.phrases_font = pg.font.Font('../assets/fonts/AlloyInk-nRLyO.ttf', 60)

        self.game_over = False
        self.flying = False

        self.faster_whisper_recording = False

        # font colors
        self.buttontext_color = '#654E56'
        self.buttontext_hover_color = '#528A2C'

        self.sentence = 'You are happy, you are strong, you are amazing'
        self.silence = 'Please be silent for 10 seconds'
        self.sentence_color = '#FFFFFF'
        self.sentence_read_color = '#0A2472'

        self.json_file_path = 'level_settings.json'
        self.csv_file_path = 'player_data.csv'
        self.phrases_path = '../assets/words/phrases.yaml'


class Constants:
    def __init__(self):
        self.ground_scroll = 0
        self.scroll_speed = 6
        self.target_fps = 60
        # self.settings = settings

        # bird constants
        self.bird_vel = 0
        self.bird_start_x = 400
        self.bird_start_y = 350
        self.bird_flap = False
        self.bird_alive = True

        # pipe constants
        self.pipe_gap = 300
        self.pipe_frequency = 1.75

        # speech constants
        # define recorder settings
        self.channels = 1
        self.frame_rate_audio = 16000
        self.chunk = 1024

        self.type_of_recording_setting = "vad"

        self.overlap_control = 2
        self.number_of_frames_in_chunk_words = 8 # corresponds to 0.48 seconds; 24 frames corresponds to 0.72 seconds; 32 frames corresponds to 0.96 seconds

        self.number_of_frames_in_chunk_sentence = 60 # corresponds to 3 seconds

        self.record_seconds_words = 0.5
        # This is the amount of seconds to record and transcribe. If it's too high it results
        # in high latency. If it's too low, it results in inaccurate transcription due to insufficient samples.
        self.record_seconds_sentence = 3

        # obstacle constants
        self.fireball_speed = 2
        self.fireball_width = 150
        self.fireball_height = 70

        self.bird_fireball_start_x = 300
        self.bird_fireball_start_y = 300

        self.last_phrase_interval = 2
        self.last_fireball_interval = 2

        # color for the command
        self.not_recognized_color = '#BCB162'
        self.recognized_color = '#313968'

        # scores for each level
        self.max_pipes_score = 5
        self.max_fireballs_score = 5

