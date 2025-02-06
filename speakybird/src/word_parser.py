from threading import Event
from whisper.normalizers import EnglishTextNormalizer

import global_var
normalizer = EnglishTextNormalizer()

def compare(word1, word2):
    # remove = string.punctuation + string.whitespace
    word1 = normalizer(word1).lstrip().rstrip()
    word2 = normalizer(word2).lstrip().rstrip()
    return word1 == word2

def remove_punctuation(sentence):
    sentence = normalizer(sentence).lstrip().rstrip()
    return sentence

# Class to parse the output of speech to text model and determine if the word in the game was spoken or not.
class Parser:
    def __init__(self):
        self.stop_event = Event()
        self.found_result = False
        self.is_command = []
        self.sentence_idx = 0
        self.update_words()
        self.is_pipe = False
        self.is_fireball = False
        self.is_staircase = True
        self.words = None
        self.recognized_command = set()

    # Returns true if the word being searched was spoken.
    def update_words(self):
        if global_var.level_settings.get_setting('pipes'):
            self.is_pipe = True
            self.is_fireball = False
            self.is_staircase = False
            self.words = [f'{global_var.command_pipe}']
        if global_var.level_settings.get_setting('fireball'):
            self.is_pipe = False
            self.is_fireball = True
            self.is_staircase = False
            self.words = [f'{global_var.command_fireball}']
        if global_var.level_settings.get_setting('staircase'):
            self.is_pipe = False
            self.is_fireball = False
            self.is_staircase = True
            self.words = global_var.command_stairs[self.sentence_idx]
    
    def get_sentence(self):
        return global_var.command_stairs[self.sentence_idx]
    
    def set_sentence(self):
        self.sentence_idx = min(self.sentence_idx + 1, len(global_var.command_stairs) - 1)
        self.words = global_var.command_stairs[self.sentence_idx]

    def find(self, transcription_output):
        if not transcription_output:
            pass
        else:
            if self.is_pipe or self.is_fireball:
                for phrase in transcription_output:
                    spoken_words = phrase.lower().split(' ')
                    # The current word of the game was spoken.
                    # Start looking for the next word in the sentence and return true.
                    for word in self.words:
                        if any(compare(word, spoken_word) for spoken_word in spoken_words):
                            self.is_command.append(True)
                            return self.is_command
            if self.is_staircase:
                transcription_output = remove_punctuation(transcription_output.lower())
                print(f"transcription_output in parser: {transcription_output}")
                self.words = remove_punctuation(self.words.lower())
                print(f"words in parser: {self.words}")
                print(transcription_output == self.words)
                if transcription_output == self.words and transcription_output not in self.recognized_command:
                    self.recognized_command.add(transcription_output)
                    print(f"recognized_command in parser: {self.recognized_command}")
                    self.is_command.append(True)
                    return self.is_command