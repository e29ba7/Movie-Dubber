import os
import re
import subprocess

from PyQt6.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject
from PyQt6.QtWidgets import QMessageBox


class Encode_signals(QObject):
    complete = pyqtSignal(bool)
    progress = pyqtSignal(int)
    max_progress = pyqtSignal(int)

class Encode(QRunnable):
    MAIN_ALIVE = True
    def __init__(self, delay_text_box, volume_text_box, audio_ratio_text_box, audio_text_box, video_text_box, movie, output_text_box, source_video):
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
            cmd = ['ffmpeg',
                '-i', f'"{self.video_text_box.text()}"',
                '-ss', f'"{self.delay_text_box.text()}ms"',
                '-i', f'"{self.audio_text_box.text()}"',
                '-filter_complex', f'''"[0:a:0]volume={self.volume_text_box.text()}dB[vol];[1:a]asplit=2[sc][mix];[vol][sc]sidechaincompress=threshold=0.01:ratio={self.audio_ratio_text_box.text()}:mix=1:attack=1[comp];[comp][mix]amix"''',
                '-c:v', 'copy',
                '-c:a', 'ac3',
                '-b:a', '256k',
                '-map', '0:v',
                '-map', '0:a:0',
                '-map', '1:a:0',
                '-metadata', f'"title={self.movie}"',
                '-metadata', f'"source={self.source_video}"',
                '-metadata', f'"delay={self.delay_text_box.text()}"',
                '-metadata', f'"attenuation={self.audio_ratio_text_box.text()}"',
                '-metadata', f'"volume={self.volume_text_box.text()}dB"',
                f'"{self.output_text_box.text()}/{self.movie} - [Dubbed].mkv"', 
                '-y']

            '''Run FFMPEG Subprocess'''
            self.ffmpeg = subprocess.Popen(
                ' '.join(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='UTF-8',
                shell=True
            )

            '''Get FFMPEG Subprocess output'''
            self.times = []
            first_dur = True
            for line in iter(self.ffmpeg.stdout.readline, ''):
                print(line.strip())
                if Encode.MAIN_ALIVE:
                    if 'not recognized as an internal' in line.strip():
                        self.error_message('Missing FFMPEG', 'You must have FFMPEG in your PATH, or in the Movie Dubber root directory')
                        raise FileNotFoundError
                    if 'Duration:' in line.strip() and first_dur:
                        self.dur = re.search(r'\d{2}:\d{2}:\d{2}', line.strip())
                        self.translated_duration = self.convert_time_to_ms(self.dur.group())
                        self.signals.max_progress.emit(self.translated_duration)
                    if 'time=' in line.strip():
                        self.time = re.search(r'\d{2}:\d{2}:\d{2}', line.strip())
                        self.translated_time = self.convert_time_to_ms(self.time.group())
                        self.check_and_kill_if_finished(self.translated_time)
                    if 'muxing overhead:' in line.strip():
                        self.signals.progress.emit(self.translated_duration)
                        self.signals.complete.emit(True)
                        self.kill_proc()
                else:
                    self.kill_proc()
        except ValueError: ...
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
        '''Check if encoding is finished by making a list and comparing the last value to the previous one, then kill if true'''
        self.times.append(time)
        if len(self.times) > 3:
            self.times.pop(0) # Restrict list to 3 entries
            if self.times[-1] == self.times[-2]: # Kill thread if the last two output times were the same (due to an FFMPEG error)
                self.signals.progress.emit(self.translated_duration)
                self.signals.complete.emit(False)
                self.kill_proc()
            else: self.signals.progress.emit(time)
        else: self.signals.progress.emit(time)

    def kill_proc(self):
        '''Check what OS user running and kill running process'''
        if os.name == 'nt':  # Windows
            subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.ffmpeg.pid))
        else: # Everything else
            self.ffmpeg.kill()
            self.ffmpeg.communicate()