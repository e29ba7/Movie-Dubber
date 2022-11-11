from threading import Thread

import ffmpeg
from PyQt6.QtCore import QRect, QSize, Qt, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import (QAudioOutput, QMediaPlayer, QVideoFrame,
                                QVideoSink)
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem, QVideoWidget
from PyQt6.QtWidgets import QFrame, QLabel, QSpinBox

from utils import Button, DialogWindow, Slider

#import numpy as np




class Editor(DialogWindow):
    def __init__(self, video_loc, audio_loc):
        super().__init__('', 'Dub Editor', 1291, 726)
        self._alive = True
        self.video_loc = video_loc
        self.audio_loc = audio_loc
        '''Media and audio players and accessories'''
        self.media_player = QMediaPlayer(self)
        # self.display_widget = QtWidgets.QWidget(self)
        # self.display_widget.setGeometry(QtCore.QRect(10, 10, 1271, 541))
        self.video_widget = QVideoWidget(self)
        self.video_widget.setGeometry(QRect(10, 25, 1271, 541))
        self.video_sink = self.video_widget.videoSink()
        self.audio_widget = QAudioOutput()
        self.media_player.setSource(QUrl.fromLocalFile(self.video_loc))
        self.media_player.setVideoSink(self.video_sink)
        # self.media_player.setVideoOutput(self.video_sink)
        self.media_player.setAudioOutput(self.audio_widget)
        # self.media_player.positionChanged.connect(self.set_location_slider)
        # self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.durationChanged.connect(self.initialize_metadata)
        self.video_sink.videoFrameChanged.connect(self.set_location_slider)
        self.audio_player = QMediaPlayer(self)
        self.audio_widget_2 = QAudioOutput()
        self.audio_player.setAudioOutput(self.audio_widget_2)
        self.audio_player.setSource(QUrl.fromLocalFile(self.audio_loc))
        self.audio_widget.setVolume(1.00)
        self.audio_widget_2.setVolume(1.00)
        '''Play button'''
        self.play_button = Button('', self)
        self.play_button.setGeometry(QRect(10, 573, 32, 24))
        self.play_icon = QIcon()
        self.play_icon.addFile("theme/play_pause_icon_137298.png")
        self.play_button.setIcon(self.play_icon)
        self.play_button.setIconSize(QSize(25, 25))
        self.play_button.clicked.connect(self.play_pause)
        '''Restart button'''
        self.restart_button = Button('', self)
        self.restart_button.setGeometry(QRect(50, 573, 32, 24))
        self.restart_button.setText('R/V')
        self.restart_button.clicked.connect(self.set_video_to_beginning)
        '''Restart both video and audio button'''
        self.restart_both_button = Button('', self)
        self.restart_both_button.setGeometry(QRect(90, 573, 32, 24))
        self.restart_both_button.setText('R/B')
        self.restart_both_button.clicked.connect(self.restart_audio_and_video)
        '''Restart everything button'''
        self.restart_everything_button = Button('', self)
        self.restart_everything_button.setGeometry(QRect(130, 573, 32, 24))
        self.restart_everything_button.setText("R/E")
        self.restart_everything_button.clicked.connect(self.restart_everything)
        '''Movie volume and divider'''
        self.movie_volume_label = QLabel(self)
        self.movie_volume_label.setGeometry(QRect(684, 580, 78, 13))
        self.movie_volume_label.setText('Movie Volume:')
        self.movie_volume = Slider(Qt.Orientation.Horizontal, self)
        self.movie_volume.setGeometry(QRect(767, 576, 200, 25))
        self.movie_volume.setRange(0, 100)
        self.movie_volume.setPageStep(5)
        self.movie_volume.setSliderPosition(50)
        self.movie_volume.setTracking(True)
        # self.movie_volume.setOrientation(Qt.Orientation.Horizontal)
        self.movie_volume.setTickPosition(Slider.TickPosition.TicksBothSides)
        self.movie_volume.valueChanged.connect(self.change_volume)
        self.divider = QFrame(self)
        self.divider.setGeometry(QRect(985, 576, 3, 23))
        self.divider.setFrameShape(QFrame.Shape.VLine)
        '''Attenuation label and slider'''
        self.attenuation_label = QLabel(self)
        self.attenuation_label.setGeometry(QRect(1000, 580, 65, 13))
        self.attenuation_label.setText('Attenuation:')
        self.attenuation_slider = Slider(Qt.Orientation.Horizontal, self)
        self.attenuation_slider.setGeometry(QRect(1071, 576, 200, 25))
        self.attenuation_slider.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.attenuation_slider.setMinimum(-10)
        self.attenuation_slider.setMaximum(10)
        self.attenuation_slider.setPageStep(1)
        self.attenuation_slider.setProperty("value", 0)
        self.attenuation_slider.setSliderPosition(0)
        self.attenuation_slider.setTracking(True)
        # self.attenuation_slider.setOrientation(Qt.Orientation.Horizontal)
        self.attenuation_slider.setTickPosition(Slider.TickPosition.TicksBothSides)
        '''Location slider and box'''
        self.location_slider = Slider(Qt.Orientation.Horizontal, self)
        self.location_slider.setGeometry(QRect(10, 595, 1191, 41))
        self.location_slider.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.location_slider.setMinimum(0)
        # self.location_slider.setOrientation(Qt.Orientation.Horizontal)
        self.location_slider.sliderMoved.connect(self.playback_position)
        self.location_box = QSpinBox(self)
        self.location_box.setMinimum(0)
        self.location_box.setGeometry(QRect(1210, 605, 61, 22))
        '''Movie track slider, label, and spinbox'''
        self.movie_track_slider = Slider(Qt.Orientation.Horizontal, self)
        self.movie_track_slider.setGeometry(QRect(10, 635, 1191, 41))
        # self.movie_track_slider.setOrientation(Qt.Orientation.Horizontal)
        # self.movie_track_slider.setMaximum(9999999)
        self.movie_track_slider.valueChanged.connect(self.adjust_movie_track_spinbox)
        self.movie_delay_label = QLabel(self)
        self.movie_delay_label.setGeometry(QRect(1208, 625, 65, 15))
        self.movie_delay_label.setText('Movie delay')
        self.movie_delay_label.setToolTip('Movie delay in ms, to fine tune movie position.')
        self.movie_track_spinbox = QSpinBox(self)
        self.movie_track_spinbox.setGeometry(QRect(1210, 645, 66, 22))
        # self.movie_track_spinbox.setMaximum(9999999)
        self.movie_track_spinbox.setToolTip('Movie delay in ms, to fine tune movie position.')
        self.movie_track_spinbox.valueChanged.connect(self.media_player_delay)
        # self.get_frames()
        '''Execute ui initiation'''
        self.exec()

    #################
    #|  FUNCTIONS  |#
    #################

    def initialize_metadata(self):
        # ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "C:\Users\Ghost\Desktop\Movies for dubs\Dubs\Ice.Cream.Man.1995.DVDRip.x264.mkv"
        # ^^^ Possible solution to get video frames, takes ~3 seconds though - Is not the same result as ShotCut gives ^^^
        self.probe = ffmpeg.probe(self.video_loc)
        self.video_info = next(s for s in self.probe['streams'] if s['codec_type'] == 'video')
        self.width = int(self.video_info['width'])
        self.height = int(self.video_info['height'])
        try: 
            self.num_frames = int(self.video_info['nb_frames']) # Doesn't work for mkv files
            print(self.num_frames)
        except: ...
        # self.out = (
        #         ffmpeg
        #         .input(main_ui.Ui_MainWindow.video_text_box.text())
        #         .output('pipe:', c='copy', f='null')
        #         .run(capture_stdout=True)
        # )
        # self.video = (
        #     np
        #     .frombuffer(self.out, np.uint8)
        #     .reshape([-1, self.height, self.width, 3])
        # )
        # stream = ffmpeg.Stream(ffmpeg.input(main_ui.Ui_MainWindow.video_text_box.text()))
        #####################
        self.movie_duration = self.media_player.duration()
        self.audio_duration = self.audio_player.duration()
        if self.movie_duration > self.audio_duration:
            self.location_slider.setMaximum(self.movie_duration)
            self.location_box.setMaximum(self.movie_duration)
        else:
            self.location_slider.setMaximum(self.audio_duration)
            self.location_box.setMaximum(self.audio_duration)
        # self.location_slider.setMaximum(self.movie_duration)
        self.movie_track_slider.setMaximum(self.movie_duration)
        self.movie_track_spinbox.setMaximum(self.movie_duration)
        self.first_frame = self.video_sink.videoFrame()

    def pause_media_and_audio(self):
        self.media_player.pause()
        self.audio_player.pause()

    def load_video_to_memory(self):
        ...

    def set_video_to_beginning(self):
        self.audio_player.pause()
        self.media_player.pause()
        self.media_player.setPosition(0)

    def restart_audio_and_video(self):
        self.media_player.pause()
        self.audio_player.pause()
        self.media_player.setPosition(0)
        self.audio_player.setPosition(0)

    def restart_everything(self):
        self.pause_media_and_audio()
        self.media_player.setPosition(0)
        self.audio_player.setPosition(0)
        self.location_slider.setValue(0)
        self.location_box.setValue(0)
        self.movie_track_slider.setValue(0)
        self.movie_track_spinbox.setValue(0)

    def set_location_slider(self):
        # self.video_sink.videoFrame()
        # print('new frame')
        # self.location_slider.setValue(self.video_sink.videoFrame)
        self.location_slider.setValue(self.media_player.position())
        self.location_box.setValue(self.media_player.position())

    def playback_position(self):
        self.pause_media_and_audio()
        self.media_player.setPosition(self.location_slider.value())
        self.audio_player.setPosition(self.location_slider.value())

    def change_volume(self):
        vol = float(self.movie_volume.value())
        vol = round(vol/100, 4)    ## Shift vol value 2 decimal places to the left
        print(f'{vol} ========== {type(vol)}')
        self.audio_widget.setVolume(vol)
        # self.audio_widget_2.setVolume(vol)

    def play_pause(self):
        if self.media_player.playbackState().value == 1:
            self.pause_media_and_audio()
        else:
            self.audio_player.play()
            self.play_media = Thread(target=self.play_media_when_match_delay)
            self.play_media.start()
            # self.play_media_when_match_delay()
            # self.media_player.play()

    def play_media_when_match_delay(self):
        # while self._alive == True:
        while self.audio_player.position() < self.movie_track_spinbox.value():
            if self.media_player.playbackState() == 1:
                self.media_player.pause()
            else:
                ...
        if self.audio_player.position() >= self.movie_track_spinbox.value():
            self.media_player.play()

    def media_player_delay(self):
        # self.blankie = QVideoFrame()
        # self.blankie.map(self.blankie.MapMode.ReadWrite)
        # self.first_frame.map(QVideoFrame.MapMode.ReadWrite)
        # self.first_frame.setStartTime(self.movie_track_spinbox.value() * 100)
        # self.first_frame.setEndTime(100)
        self.first_frame.setEndTime(self.movie_track_spinbox.value())
        # self.video_sink.setVideoFrame(self.first_frame)
        # print(self.first_frame.mapMode())
        if self.media_player.playbackState() == 1 or self.audio_player.playbackState() == 1:
            self.pause_media_and_audio()
        # movie_delay = self.movie_track_spinbox.value()

    def play_video(self):
        while self.audio_player.position() != self.movie_track_spinbox.value():
            ...
        if self.audio_player.position() >= self.movie_track_spinbox.value():
            self.media_player.play()

    def adjust_movie_track_spinbox(self):
        self.movie_track_spinbox.setValue(self.movie_track_slider.value())

    def confirm_options(self):
        # For when I make a confirm button
        ...

    def terminate(self):
        print('bye')