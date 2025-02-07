import time
import global_var
import numpy as np
import pyaudio
import webrtcvad
import uuid

from queue import Queue
from threading import Thread, Event
from faster_whisper import WhisperModel
from whisper.tokenizer import get_tokenizer
from word_parser import Parser
from datetime import datetime


device = "cuda"
model_name = "tiny_english"
model = WhisperModel("tiny.en", device=device)


class FasterWhisperTranscriber:
    def __init__(self, constants, plot_transcribe_time, shared_data):
        self.recordings = Queue()
        self.transcriptions = Queue()
        self.stop_event = Event()
        self.parser = Parser()
        self.constants = constants

        self.shared_data = shared_data

        self.plot_transcribe_time = plot_transcribe_time # if plot_transcribe_time == 'True' it will plot the transcribe time
        self._stop_threads = False  # Flag to signal threads to stop

        self.audio_format = pyaudio.paInt16
        self.frame_rate = self.constants.frame_rate_audio
        self.channels = self.constants.channels

        self.overlap_control = self.constants.overlap_control

        """Parameters for the VAD"""
        self.vad = webrtcvad.Vad(3)
        self.frame_in_milliseconds = 30  # Vad accepts 10, 20, 30
        self.frame_size_in_samples = int(
            self.frame_rate * self.frame_in_milliseconds / 1000)  # Vad accepts 160, 320, 480

        self.number_of_subsequence_in_sequence = 0
        self.number_of_samples_in_subsequence = self.frame_size_in_samples
        self.number_of_samples_in_sequence = 0

        self.time_for_subsequence = self.number_of_samples_in_subsequence / self.frame_rate
        self.time_for_sequence = 0

        self.record_seconds = 0

        self.type_of_recording_setting = self.constants.type_of_recording_setting
        if self.type_of_recording_setting == "baseline":
            self.is_baseline = True
            self.is_vad = False
            self.is_sequence_window = False
        elif self.type_of_recording_setting == "vad":
            self.is_baseline = False
            self.is_vad = True
            self.is_sequence_window = False
        elif self.type_of_recording_setting == "window":
            self.is_baseline = False
            self.is_vad = False
            self.is_sequence_window = True
        self.is_speech = False

        self.speech_frames = []
        self.silent_frames = []
        self.all_frames = []

        self.transcribe_result = []
        self.tokens = []

        self.data_to_plot = []
        self.signal_to_plot = []

        self.signal_to_plot_in_transcriber = []
        self.transcribe_times_to_plot = []

        self.transcribe_result_plot = []

        self.chunk_counter = 0
        # self.chunk_counter_transcriber = 0
        self.transcription_iteration = []

        self.transcriber_audio_dictionary = {}

        self.is_command = None
        self.is_fireball = False
        self.is_pipes = False
        self.is_staircase = False
        self.command = ""
        self.initial_prompt = ""
        self.hotword = ""

        self.overlap = 0
        self.number_of_overlap_subsequences = 0

        self.overlap_frames = []
        self.window_function = []

        # self.number_of_frames_per_chunk = (self.constants.frame_rate_audio * self.record_seconds) // self.frame_size_in_samples
        self.number_of_frames_per_chunk = 0


    def record_audio_baseline(self):
        try:
            print('Recording audio in faster_whisper baseline')
            audio = pyaudio.PyAudio()

            # get the index of the default microphone device
            default_device = audio.get_default_input_device_info()
            default_device_index = default_device.get('index')

            # record audio from the microphone
            stream = audio.open(format=self.audio_format, channels=self.constants.channels,
                                rate=self.frame_rate,
                                input=True,
                                input_device_index=default_device_index, frames_per_buffer=self.number_of_subsequence_in_sequence)

            while not self.stop_event.is_set():
                start_time = time.time()
                input_stream_in_bytes = stream.read(self.number_of_samples_in_sequence)
                input_signal = np.frombuffer(input_stream_in_bytes, dtype=np.int16)

                print(f"Length of input signal: {len(input_signal)}")

                self.signal_to_plot.append(input_signal)
                # self.all_frames.append(input_signal)

                current_time = time.time() - start_time
                unique_id = str(uuid.uuid4())

                # print(f"            length of all frames before sending: {len(self.all_frames)}")
                # Send the combined_frame_transcriber to the queue
                self.recordings.put({
                    "id": unique_id,
                    "frames": input_signal,  # Send the combined frame with overlap
                    "counter": self.chunk_counter,
                    "time": current_time
                })

                self.chunk_counter += 1
                subsequence_counter = 0

                # # Clear the frames and silent_frames for the next chunk
                self.speech_frames = []
                self.silent_frames = []
                # self.all_frames = []
        except Exception as e:
            print(f"Error in recording audio baseline: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

    def record_audio_window(self):
        try:
            print('Recording audio in faster_whisper')
            audio = pyaudio.PyAudio()

            # get the index of the default microphone device
            default_device = audio.get_default_input_device_info()
            default_device_index = default_device.get('index')

            # record audio from the microphone
            stream = audio.open(format=self.audio_format, channels=self.constants.channels,
                                rate=self.frame_rate,
                                input=True,
                                input_device_index=default_device_index, frames_per_buffer=self.number_of_subsequence_in_sequence)

            while not self.stop_event.is_set():
                start_time = time.time()
                input_stream_in_bytes = stream.read(self.number_of_samples_in_sequence)
                input_signal = np.frombuffer(input_stream_in_bytes, dtype=np.int16)


                self.signal_to_plot.append(input_signal)

                input_signal_with_overlap = np.concatenate((self.overlap_frames, input_signal))
                input_signal_windowed = input_signal_with_overlap * self.window_function
                self.all_frames.append(input_signal_windowed)
                self.overlap_frames = input_signal_with_overlap[-self.overlap:]

                # self.all_frames.append(input_signal)

                current_time = time.time() - start_time
                unique_id = str(uuid.uuid4())

                # Send the combined_frame_transcriber to the queue
                self.recordings.put({
                    "id": unique_id,
                    "frames": self.all_frames,  # Send the combined frame with overlap
                    "counter": self.chunk_counter,
                    "time": current_time
                })

                self.chunk_counter += 1
                subsequence_counter = 0

                # # Clear the frames and silent_frames for the next chunk
                self.speech_frames = []
                self.silent_frames = []
                self.all_frames = []
        except Exception as e:
            print(f"Error in recording audio baseline: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

    def record_audio_window_and_vad(self):
        try:
            print(self.command)
            audio = pyaudio.PyAudio()

            # get the index of the default microphone device
            default_device = audio.get_default_input_device_info()
            default_device_index = default_device.get('index')

            # record audio from the microphone
            stream = audio.open(format=self.audio_format, channels=self.constants.channels,
                                rate=self.frame_rate,
                                input=True,
                                input_device_index=default_device_index, frames_per_buffer=self.number_of_subsequence_in_sequence)

            while not self.stop_event.is_set():
                start_time = time.time()
                input_stream_in_bytes = stream.read(self.number_of_samples_in_sequence)
                input_signal = np.frombuffer(input_stream_in_bytes, dtype=np.int16)

                self.signal_to_plot.append(input_signal)

                input_signal_with_overlap = np.concatenate((self.overlap_frames, input_signal))
                length_of_signal_after_overlap = len(input_signal_with_overlap)
                indices = np.arange(0, length_of_signal_after_overlap, self.number_of_samples_in_subsequence)

                for ii in indices:
                    subsequence_array = input_signal_with_overlap[ii:ii + self.number_of_samples_in_subsequence]
                    is_speech = self.vad.is_speech(subsequence_array.tobytes(), self.constants.frame_rate_audio)
                    if is_speech:
                        self.speech_frames.append(subsequence_array)
                    else:
                        self.silent_frames.append(subsequence_array)

                self.overlap_frames = input_signal_with_overlap[-self.overlap:]

                current_time = time.time() - start_time
                unique_id = str(uuid.uuid4())
                if not self.speech_frames:
                    self.speech_frames = []
                    self.silent_frames = []
                    self.all_frames = []

                else:
                    self.recordings.put({
                        "id": unique_id,
                        "frames": self.speech_frames,  # Send the combined frame with overlap
                        "counter": self.chunk_counter,
                        "time": current_time
                    })

                # # Clear the frames and silent_frames for the next chunk
                    self.speech_frames = []
                    self.silent_frames = []
                    self.all_frames = []
                self.chunk_counter += 1
        except Exception as e:
            print(f"Error in recording audio vad: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

    def tokenize_text(self):
        text = ['and', ' beep', 'party', ' and the game is so good!', ' [Music]', ' (bell rings)', ' *', ' free', ' b', ' peek',' .', ' . . .',
                ' "The End"', ' be', 'bam', ' Hi', ' Thank you.', ' Bye bye.', ' have it', ' hi', ' hahaha', ' me', ' bye', ' hello', ' ',
                ' a', ' c', ' d', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '!', '?', '.', ',', 'ok', 'Dangit',
                ' thank You for watching this video', 'And then we\'ll see how that will happen in our next episode of Clevver News', ' ah', ' hey', ' ok', ' See ya later !', ' t-', ' pew',
                'output', 'also', 'single', 'word', 'after', 'colon', 'command', 'ignore', '[MUSIC]']
        t = get_tokenizer(False)
        unique_tokens = set()  # Use a set to store unique tokens

        for txt in text:
            tokenized_text = t.encode(txt)

            # Add each token to the set
            for token in tokenized_text:
                unique_tokens.add(token)

        if self.is_pipes or self.is_fireball:
            self.tokens = list(unique_tokens)
        if self.is_staircase:
            self.tokens = [-1]


    def transcribe_audio(self):
        while not self.stop_event.is_set():
            frames = self.recordings.get()
            audio_frames = frames["frames"]
            unique_id = frames["id"]
            counter = frames["counter"]
            with self.shared_data['lock']:
                self.shared_data['transcribe_start_time'] = time.perf_counter()

            if self.is_baseline:
                audio = audio_frames.astype(np.float32) / 32768.0

            else:
                audio = np.concatenate(audio_frames)
                audio = audio.astype(np.float32) / 32768.0
            start_time = time.time()

            segments, info = model.transcribe(audio, beam_size=5, hotwords=f"{self.hotword}", language="en",
                                              condition_on_previous_text=False,
                                              initial_prompt=f"{self.initial_prompt}",
                                              temperature=0.2, prompt_reset_on_temperature=True, repetition_penalty=1.5,
                                              length_penalty=2, suppress_tokens=self.tokens, suppress_blank=True)
            end_time = time.time()
            total_time = end_time - start_time

            for segment in segments:
                self.transcribe_result.append(segment.text)
                print(f"segment text: {self.transcribe_result[-1]}")

            if not self.transcribe_result:
                self.transcribe_result_plot.append((counter, total_time, "No Speech"))
            elif self.transcribe_result[-1] != "":
                stripped_text = self.transcribe_result[-1].strip()  # Remove leading and trailing whitespace
                if self.transcribe_result:
                    self.transcribe_result_plot.append((counter, total_time, stripped_text))
                words = stripped_text.split()
                print(f"words: {words}")
                if self.is_pipes or self.is_fireball:
                    if len(words) > 1:
                        print(f"transcribe result before popping: {self.transcribe_result}")
                        self.transcribe_result.pop()
                        print(f"transcribe result after popping: {self.transcribe_result}")
                    self.is_command = self.parser.find(self.transcribe_result)
                else:
                    self.is_command = self.parser.find(stripped_text)
            self.transcribe_times_to_plot.append(total_time)
            self.transcription_iteration.append(counter)

            time.sleep(0.01)
            frames = []
            self.transcribe_result = []

    def start_recording(self):  #self, rms_speech, db_speech, rms_silence, db_silence
        self.set_level_settings()
        self.parser.update_words()
        self._stop_threads = False
        if self.is_vad:
            record = Thread(name='record', target=self.record_audio_window_and_vad, daemon=True)
            record.start()
        elif self.is_baseline:
            record = Thread(name='record', target=self.record_audio_baseline, daemon=True)
            record.start()
        elif self.is_sequence_window:
            record = Thread(name='record', target=self.record_audio_window, daemon=True)
            record.start()

        transcribe = Thread(name='transcribe', target=self.transcribe_audio, daemon=True)
        transcribe.start()

    def set_level_settings(self):
        if global_var.level_settings.get_setting('pipes'):
            self.is_pipes = True
            self.is_fireball = False
            self.is_staircase = False
            self.command = f'{global_var.command_pipe}'
            self.record_seconds = self.constants.number_of_frames_in_chunk_words * (self.frame_in_milliseconds / 1000)
            self.initial_prompt = f"ignore silence and noise. Single word after colon: {self.command}"
            self.hotword = self.command
            self.number_of_subsequence_in_sequence = self.constants.number_of_frames_in_chunk_words
            self.number_of_samples_in_sequence = self.number_of_samples_in_subsequence * self.number_of_subsequence_in_sequence
            self.time_for_sequence = self.number_of_samples_in_sequence / self.constants.frame_rate_audio

            if not self.is_baseline:
                self.overlap = int(self.number_of_samples_in_sequence // self.overlap_control)
                self.overlap_frames = np.zeros(self.overlap, dtype=np.int16)
                self.window_function = np.hamming(self.number_of_samples_in_sequence + self.overlap)
                self.number_of_overlap_subsequences = self.overlap // self.number_of_samples_in_subsequence

        if global_var.level_settings.get_setting('fireball'):
            self.is_fireball = True
            self.is_pipes = False
            self.is_staircase = False
            self.command = f'{global_var.command_fireball}'
            self.record_seconds = self.constants.number_of_frames_in_chunk_words * (self.frame_in_milliseconds / 1000)
            self.initial_prompt = f"Single word after colon: {self.command}"
            self.hotword = self.command
            self.number_of_frames_per_chunk = self.constants.number_of_frames_in_chunk_words
            self.number_of_subsequence_in_sequence = self.constants.number_of_frames_in_chunk_words
            self.number_of_samples_in_sequence = self.number_of_samples_in_subsequence * self.number_of_subsequence_in_sequence
            self.time_for_sequence = self.number_of_samples_in_sequence / self.constants.frame_rate_audio

            if not self.is_baseline:
                self.overlap = int(self.number_of_samples_in_sequence // self.overlap_control)
                self.overlap_frames = np.zeros(self.overlap, dtype=np.int16)
                self.window_function = np.hamming(self.number_of_samples_in_sequence + self.overlap)
                self.number_of_overlap_subsequences = self.overlap // self.number_of_samples_in_subsequence

        if global_var.level_settings.get_setting('staircase'):
            self.is_staircase = True
            self.is_fireball = False
            self.is_pipes = False
            self.command = f'{global_var.command_stairs}'
            self.record_seconds = self.constants.number_of_frames_in_chunk_sentence * (
                        self.frame_in_milliseconds / 1000)
            self.initial_prompt = f'is one of the sentences in {self.command}'
            self.hotword = ''
            self.number_of_frames_per_chunk = self.constants.number_of_frames_in_chunk_sentence
            self.number_of_subsequence_in_sequence = self.constants.number_of_frames_in_chunk_sentence
            self.number_of_samples_in_sequence = self.number_of_samples_in_subsequence * self.number_of_subsequence_in_sequence
            self.time_for_sequence = self.number_of_samples_in_sequence / self.constants.frame_rate_audio

            if not self.is_baseline:
                self.overlap = int(self.number_of_samples_in_sequence // self.overlap_control)
                self.overlap_frames = np.zeros(self.overlap, dtype=np.int16)
                self.window_function = np.hamming(self.number_of_samples_in_sequence + self.overlap)
                self.number_of_overlap_subsequences = self.overlap // self.number_of_samples_in_subsequence

    def output(self):
        if self.is_command:
            command = self.is_command.pop(0)  # Pop the first element
            return command
        else:
            return False

    def clear_transcribe_result(self):
        self.transcribe_result = []

    def stop_recording(self):
        # self.messages.get()
        self.stop_event.set()
        self._stop_threads = True
        self.recordings = Queue()
        self.transcriptions = Queue()

        ## Uncomment incase you want to save the transcribe times to a csv file

        # current_date = datetime.now().strftime("%d-%m-%y")
        # current_time = datetime.now().strftime("%H-%M-%S")
        # headers = ["Iteration", "Transcribe Time", "Transcription Result"]
        # data = list(zip(self.transcription_iteration, self.transcribe_times_to_plot, self.transcribe_result_plot))
        # directory = f"output/csv_files/transcribe_time/{current_date}/{self.command}/{self.type_of_recording_setting}/{model_name}/{self.number_of_subsequence_in_sequence}/{self.overlap_control}/"
        # filename_prefix = "transcription_times"
        # save_data_to_csv(directory, filename_prefix, data, headers)

    def get_parser(self):
        return self.parser

