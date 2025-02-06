import os
import time
from queue import Queue
from threading import Thread

import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import torch
import whisper

model = whisper.load_model("tiny.en")


class WhisperTranscriber:
    def __init__(self, settings, constants, plot_transcribe_time):
        self.recordings = Queue()
        self.transcribe_result = []
        self.AUDIO_FORMAT = pyaudio.paInt16
        self.settings = settings
        self.constants = constants
        self._stop_threads = False  # Flag to signal threads to stop
        self.transcribe_times = []
        self.plot_transcribe_time = plot_transcribe_time

        self.transcribe_result_plot = []

        # self.web_rtc_vad = webrtcvad.Vad(3)
        #
        # self.FRAME_DURATION_MS = 10
        # self.FRAME_SIZE = int(self.constants.frame_rate_audio * self.FRAME_DURATION_MS / 1000)  # Frame size in samples
        # self.CHUNK = self.FRAME_SIZE * 2  # 320 samples

    # def record_audio(self, chunk=1024):
    #     print('Recording audio')
    #     audio = pyaudio.PyAudio()
    #
    #     # get the index of the default microphone device
    #     default_device = audio.get_default_input_device_info()
    #     default_device_index = default_device.get('index')
    #
    #     # record audio from the microphone
    #     stream = audio.open(format=self.AUDIO_FORMAT, channels=self.constants.channels,
    #                         rate=self.constants.frame_rate_audio,
    #                         input=True,
    #                         input_device_index=default_device_index, frames_per_buffer=self.FRAME_SIZE)
    #
    #     frames = []
    #     silent_frames = []
    #
    #     while not self._stop_threads:
    #         data = stream.read(self.CHUNK)
    #         assert (len(data) >= self.CHUNK)
    #
    #         if len(data) >= self.CHUNK:
    #             is_speech = self.web_rtc_vad.is_speech(data, self.constants.frame_rate_audio)
    #             stream_array = np.frombuffer(data, dtype=np.int16)
    #             if is_speech:
    #                 frames.append(stream_array)
    #             else:
    #                 silent_frames.append(stream_array)
    #
    #         if (len(frames) + len(silent_frames) >= (self.constants.frame_rate_audio * self.constants.record_seconds)
    #                 / self.CHUNK):
    #             self.recordings.put(frames.copy())
    #             frames = []
    #             silent_frames = []
    #
    #     stream.stop_stream()
    #     stream.close()
    #     audio.terminate()
    def record_audio(self, chunk=1024):
        print('Recording audio')
        audio = pyaudio.PyAudio()

        # get the index of the default microphone device
        default_device = audio.get_default_input_device_info()

        default_device_index = default_device.get('index')

        # record audio from the microphone
        stream = audio.open(format=self.AUDIO_FORMAT, channels=self.constants.channels,
                            rate=self.constants.frame_rate_audio,
                            input=True,
                            input_device_index=default_device_index, frames_per_buffer=chunk)

        frames = []

        while not self._stop_threads:  # Check flag to stop threads
            data = stream.read(chunk)

            # read buffer as 1D array
            stream_array = np.frombuffer(data, dtype=np.int16)

            frames.append(stream_array)

            if len(frames) >= (self.constants.frame_rate_audio * self.constants.record_seconds) / chunk:
                self.recordings.put(frames.copy())
                frames = []

        stream.stop_stream()
        stream.close()
        audio.terminate()

    def speech_to_text(self):
        try:
            print('Transcribing audio')
            while not self._stop_threads:
                frames = self.recordings.get()
                # if not frames:
                #     print("Silent Frames")
                #     continue
                frames = np.asarray(frames).flatten()

                # normalize by dividing by 2^15 to convert wav to float32 array
                frames = frames.astype(np.float32) / 32768.0
                start_time = time.time()
                result = model.transcribe(frames, language="en", fp16=torch.cuda.is_available(),
                                          initial_prompt="only single word commands for the game: up down",
                                          verbose=True,
                                          hallucination_silence_threshold=0.3)
                end_time = time.time()
                self.transcribe_times.append(end_time - start_time)
                if len(result["text"]) > 0:
                    self.transcribe_result.append(result["text"])

                print(f"Transcribe result: {self.transcribe_result}")
                if not self.transcribe_result:
                    self.transcribe_result_plot.append((self.transcribe_times[-1], "No Speech"))
                else:
                    self.transcribe_result_plot.append((self.transcribe_times[-1], result["text"].strip()))

        except RuntimeError:
                print("Restarting transcribe")
                self.speech_to_text()

    def start_recording(self):
        print('Recording started')
        self._stop_threads = False  # Clear the stop flag before starting
        self.recordings.put(True)
        record = Thread(target=self.record_audio)
        record.start()

        transcribe = Thread(target=self.speech_to_text)
        transcribe.start()

    def output(self):
        return self.transcribe_result

    def clear_transcribe_result(self):
        self.transcribe_result.clear()

    def stop_recording(self):
        self._stop_threads = True
        self.recordings = Queue()
        max_value = max(self.transcribe_times)
        if self.plot_transcribe_time:
            print(self.transcribe_times)
            plt.stem(self.transcribe_times)
            plt.xlabel("Instance")
            plt.ylabel("Transcribe Time (sec)")
            plt.title("Whisper Transcribe Time")
            plt.yticks(np.arange(0, max_value, step=0.2))

            for idx, time_text_pair in enumerate(self.transcribe_result_plot):
                time_t, text = time_text_pair
                plt.text(idx, time_t, text, rotation=90)

            folder_path = "../outputs/plots/"

            # Create the folder if it doesn't exist
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, "whisper_cuda.png")
            plt.savefig(file_path)

            plt.show()
