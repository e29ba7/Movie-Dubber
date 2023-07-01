import os
import re
import subprocess

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMessageBox

from utils import ErrorDialog


class Encode_signals(QObject):
    complete = pyqtSignal(bool)
    progress = pyqtSignal(int)
    max_progress = pyqtSignal(int)

class Encode(QRunnable):
    MAIN_ALIVE = True
    def __init__(
        self,
        delay_text_box,
        volume_text_box,
        audio_ratio_text_box,
        audio_text_box,
        video_text_box,
        movie,
        output_text_box,
        source_video
        ):
        super().__init__()
        self.delay_text_box = delay_text_box
        self.volume_text_box = volume_text_box
        self.audio_ratio_text_box = audio_ratio_text_box
        self.audio_text_box = audio_text_box
        self.video_text_box = video_text_box
        self.movie = movie
        self.output_text_box = output_text_box
        self.source_video = source_video
        self.signals = Encode_signals()

    @pyqtSlot()
    def run(self):
        try:
            '''FFMPEG Command line options'''
            cmd = [
                'ffmpeg',
                '-i', f'"{self.video_text_box.text()}"',
                '-ss', f'"{self.delay_text_box.text()}ms"',
                '-i', f'"{self.audio_text_box.text()}"',
                '-filter_complex', f'''\
                    "[0:a:0]volume={self.volume_text_box.text()}dB[vol];\
                    [vol]sidechaincompress=threshold=0.01:\
                    ratio={self.audio_ratio_text_box.text()}:\
                    mix=1:attack=1:release=500[comp];\
                    [comp][1:a]amix=inputs=2"''',
                '-c:v', 'copy',
                '-c:s', 'copy',
                '-c:a', 'ac3',
                '-b:a', '256k',
                '-map', '0:v',
                '-map', '0:a',
                '-map', '1:a',
                '-metadata', f'"title={self.movie}"',
                '-metadata', f'"source={self.source_video}"',
                '-metadata', f'"delay={self.delay_text_box.text()}"',
                '-metadata', f'"attenuation={self.audio_ratio_text_box.text()}"',
                '-metadata', f'"volume={self.volume_text_box.text()}dB"',
                f'"{self.output_text_box.text()}/{self.movie} - [Dubbed].mkv"', 
                '-y'
                ]

            '''Open FFMPEG subprocess'''
            self.ffmpeg = subprocess.Popen(
                ' '.join(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='UTF-8',
                shell=True
                )

            '''Get FFMPEG subprocess output'''
            self.times = [] # For check_and_kill_if_finished()
            first_duration = True
            for line in iter(self.ffmpeg.stdout.readline, ''):
                print(line.strip())
                if Encode.MAIN_ALIVE:
                    if 'not recognized as an internal' in line.strip():
                        ErrorDialog('Missing FFMPEG', 'You must have FFMPEG in your PATH, or in the Movie Dubber root directory')
                        raise FileNotFoundError
                    if 'Duration:' in line.strip() and first_duration:
                        self.duration = re.search(r'\d{2}:\d{2}:\d{2}', line.strip())
                        self.translated_duration = self.convert_time_to_ms(self.duration.group())
                        self.signals.max_progress.emit(self.translated_duration)
                    if 'time=' in line.strip():
                        self.time = re.search(r'\d{2}:\d{2}:\d{2}', line.strip())
                        self.translated_time = self.convert_time_to_ms(self.time.group())
                        self.check_and_kill_if_finished(self.translated_time)
                    if 'muxing overhead:' in line.strip():
                        self.signals.progress.emit(self.translated_duration)
                        self.signals.complete.emit(True)
                        self.kill_process()
                else:
                    self.kill_process()
        except FileNotFoundError: ...

    #################
    #|  FUNCTIONS  |#
    #################

    def error_message(self, title, text):
        self.error = QMessageBox(parent=self, text=text)
        self.error.setWindowTitle(title)
        self.error.exec()

    def convert_time_to_ms(self, time):
        '''Convert XX:XX:XX time string format to milliseconds (int)'''
        self.hour, self.minute, self.second = [int(i) for i in time.split(':')]
        return (self.hour*3600 + self.minute*60 + self.second) * 1000

    def check_and_kill_if_finished(self, time):
        '''Check if encoding is finished by making a list and comparing
        the last value to the previous one, then kill if they're same time
        (Fixes FFMPEG issue)'''
        self.times.append(time)
        if len(self.times) > 3:
            self.times.pop(0) # Restrict list to 3 entries
            if self.times[-1] == self.times[-2]: # Kill thread if the last two output times were the same (due to FFMPEG loop error)
                self.signals.progress.emit(self.translated_duration)
                self.signals.complete.emit(False)
                self.kill_process()
            else: self.signals.progress.emit(time)
        else: self.signals.progress.emit(time)

    def kill_process(self):
        '''Check what OS user running and kill running process'''
        if os.name == 'nt':  # Windows systems
            subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.ffmpeg.pid))
        else: # Everything else
            self.ffmpeg.kill()
            self.ffmpeg.communicate()