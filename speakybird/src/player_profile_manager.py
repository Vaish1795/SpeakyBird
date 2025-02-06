# Maintains user profile and scores for the game.
import json
import os

import global_var


class ScoreManager:
    def __init__(self, file_path, sound):
        self.file_path = file_path
        self.sounds = sound
        self.score = 0
        self.load_score()

    def load_score(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                self.score = data.get("score", 0)

    def save_score(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                data = json.load(file)
        else:
            data = {}

        data["score"] = self.score

        with open(self.file_path, 'w') as file:
            json.dump(data, file)

    def increment_score(self, points=1):
        self.score += points
        print(f'is combined {global_var.level_settings.get_setting("combined")}')
        if global_var.level_settings.get_setting("sound") and not global_var.level_settings.get_setting("staircase"):
            self.sounds['point'].play()
        self.save_score()

    def decrement_score(self, points=1):
        self.score -= points
        if global_var.level_settings.get_setting("sound"):
            self.sounds['hit'].play()
        if self.score < 0:
            self.score = 0
        self.save_score()

    def update_score(self, final_score):
        self.score = final_score
        self.save_score()

    def get_score(self):
        return self.score

    def reset_score(self):
        self.score = 0
        self.save_score()
        return self.score

class LevelSettings:
    def __init__(self, file_path):
        self.file_path = file_path
        self.settings = {
            "player_name": global_var.name,
            "avatar_path": '../assets/images/avatars/1.png',
            "sound": False,
            "language": "english",
            "keyboard": False,
            "voice": True,
            "pipes": True,
            "fireball": False,
            "combined": False,
            "staircase": False,
        }
        self.default_settings = self.settings.copy()
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                self.settings = json.load(file)

    def save_settings(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.settings, file)

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def get_setting(self, key):
        return self.settings.get(key)

    def reset_to_defaults(self):
        self.settings = self.default_settings.copy()
        self.save_settings()

