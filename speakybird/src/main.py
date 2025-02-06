import argparse
import sys

import pygame as pg

import screens
import settings


def handle_keyboard_interrupt():
    print("Keyboard interrupt received. Exiting the game")
    pg.quit()
    sys.exit()


if __name__ == '__main__':
    try:
        pg.init()
        parser = argparse.ArgumentParser()
        parser.add_argument("--model", choices=['whisper', 'faster_whisper'], default='faster_whisper')
        parser.add_argument("--plot_transcribe_time", choices=['False', 'True'], default='True')
        args = parser.parse_args()
        settings_ = settings.Settings()
        constants = settings.Constants()
        game = screens.Screens('faster_whisper', args.plot_transcribe_time, settings_, constants)

        game.start_menu()
    except KeyboardInterrupt:
        handle_keyboard_interrupt()
        sys.exit()

