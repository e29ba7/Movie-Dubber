import re

from PyQt6.QtCore import QRect, QRegularExpression, QThreadPool
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QFileDialog, QLineEdit, QProgressBar

import encoder
from database import database_ui
from media_editor import Editor
from utils import Button, DialogWindow, ErrorDialog


class MainWindow(DialogWindow):
    def __init__(self):
        super().__init__('popcorn.ico', 'Movie Dubber', 271, 176)
        '''Titlebar tooltip - Author'''
        self.tb_title.setToolTip("Made by f09f9095")
        '''Titlebar buttons'''
        self.minimize_button = Button('-', self.central_widget)
        self.minimize_button.setGeometry(QRect(230, 4, 16, 16))
        self.minimize_button.clicked.connect(self.showMinimized)
        self.minimize_button.setStyleSheet("""
            border: 1px solid #444444;
            border-radius: 4px;"""
            )
        '''Output button'''
        self.output_button = Button('Output', self.central_widget)
        self.output_button.setGeometry(QRect(10, 25, 61, 21))
        self.output_button.setToolTip("Select file output location")
        self.output_button.clicked.connect(self.output_file_location)
        '''Output text box'''
        self.output_text_box = QLineEdit(self.central_widget)
        self.output_text_box.setGeometry(QRect(80, 25, 181, 21))
        self.output_text_box.setToolTip("Select folder where output will be saved")
        self.output_text_box.setPlaceholderText("Select Output Location")
        '''Delay text box'''
        self.delay_text_box = QLineEdit(self.central_widget)
        self.delay_text_box.setGeometry(QRect(10, 55, 96, 21))
        self.delay_text_box.setPlaceholderText("Delay (ms)")
        self.delay_text_box.setToolTip("Enter movie delay in milliseconds")
        self.delay_text_box.setValidator(QRegularExpressionValidator(QRegularExpression(r'\d{6}')))
        '''Volume text box'''
        self.volume_text_box = QLineEdit(self.central_widget)
        self.volume_text_box.setGeometry(QRect(115, 55, 67, 21))
        self.volume_text_box.setToolTip("""
            <p>Enter volume change in dB (integer).
            Can be negative. E.g. '5 or -3'</p>"""
            )
        self.volume_text_box.setPlaceholderText("Volume")
        self.volume_text_box.setValidator(QRegularExpressionValidator(QRegularExpression(r'\d{2}')))
        '''Audio ratio text box'''
        self.audio_ratio_text_box = QLineEdit(self.central_widget)
        self.audio_ratio_text_box.setGeometry(QRect(191, 55, 70, 21))
        self.audio_ratio_text_box.setToolTip("""
            <p>Enter ratio to attenuate
            (While added audio is talking,
            the movie track will temporarily drown out)
            E.g. 2.5 (Range: 1 - 9.99)</p>"""
            )
        self.audio_ratio_text_box.setPlaceholderText("Ratio")
        self.audio_ratio_text_box.setValidator(QRegularExpressionValidator(QRegularExpression(r'\d\.\d{2}')))
        '''Video button'''
        self.video_Button = Button('Video File', self.central_widget)
        self.video_Button.setGeometry(QRect(10, 85, 61, 21))
        self.video_Button.setToolTip("Select video input")
        self.video_Button.clicked.connect(self.get_video_file)
        '''Video text box'''
        self.video_text_box = QLineEdit(self.central_widget)
        self.video_text_box.setGeometry(QRect(80, 86, 181, 21))
        self.video_text_box.setToolTip("Select video input")
        self.video_text_box.setPlaceholderText('Select Video File')
        '''Audio button'''
        self.audio_button = Button('Audio File', self.central_widget)
        self.audio_button.setGeometry(QRect(10, 115, 61, 21))
        self.audio_button.setToolTip("Select audio input to overlay")
        self.audio_button.clicked.connect(self.get_audio_file)
        '''Audio text box'''
        self.audio_text_box = QLineEdit(self.central_widget)
        self.audio_text_box.setGeometry(QRect(80, 115, 181, 21))
        self.audio_text_box.setToolTip("Select audio input to overlay")
        self.audio_text_box.setPlaceholderText('Select Audio Track')
        '''Load button'''
        self.load_button = Button('Load', self.central_widget)
        self.load_button.setGeometry(QRect(10, 145, 50, 21))
        self.load_button.setToolTip("Load sync information from database.")
        self.load_button.clicked.connect(self.open_database)
        '''Encode button'''
        self.encode_button = Button('Encode', self.central_widget)
        self.encode_button.setGeometry(QRect(65, 145, 56, 21))
        self.encode_button.setToolTip("Begin encoding process")
        self.encode_button.clicked.connect(self.check_inputs_and_encode)
        '''Editor button (Editor is not enabled)'''
        self.editor_button = Button('E', self.central_widget)
        self.editor_button.setGeometry(QRect(207, 4, 16 ,16))
        self.editor_button.setToolTip("The editor isn't ready yet.")
        self.editor_button.setDisabled(True)
        self.editor_button.setDefault(True)
        self.editor_button.hide()
        self.editor_button.clicked.connect(self.start_editor)
        '''Progress bar'''
        self.progress_bar = QProgressBar(self.central_widget)
        self.progress_bar.setGeometry(QRect(130, 145, 131, 21))
        self.progress_bar.setMinimum(0)
        '''Run'''
        self.show()

    #################
    #|  FUNCTIONS  |#
    #################

    def get_video_file(self):
        self.video_file = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select Video File',
            filter='Video files (*.mkv *.mp4 *.avi *.mov )'
            )
        self.video_text_box.setText(self.video_file[0])

    def get_audio_file(self):
        self.audio_file = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select Audio File',
            filter='Audio files (*.mp3 *.m4a)'
            )
        self.audio_text_box.setText(self.audio_file[0])

    def output_file_location(self):
        self.save_loc = QFileDialog.getExistingDirectory(
            parent=self,
            caption='Select save location'
            )
        self.output_text_box.setText(self.save_loc)

    def open_database(self):
        try:
            self.data = database_ui.Ui_Database().data
            self.movie = self.data[0]
            self.delay_text_box.setText(str(self.data[3]))
            self.audio_ratio_text_box.setText(str(self.data[4]))
            self.volume_text_box.setText(str(self.data[5]))
        except IndexError: ...

    def check_inputs_and_encode(self):
        try:
            self.disable_encode_button()
            '''Check Delay, Volume, and Ratio text boxes'''
            if "/" not in self.output_text_box.text():
                ErrorDialog('Output location error', 'You must select an output location folder.')
                raise ValueError
            if not re.match(r'\d', self.delay_text_box.text()):
                ErrorDialog('Delay error', 'You must provide a delay in milliseconds')
                raise ValueError
            if not re.match(r'\d', self.volume_text_box.text()):
                self.volume_text_box.setText('0')
            if not re.match(r'\d', self.audio_ratio_text_box.text()):
                self.audio_ratio_text_box.setText('1')
            if "/" in self.video_text_box.text():
                self.source_video = re.split("/", self.video_text_box.text())[-1]
            else:
                ErrorDialog('Video source error', 'You must select a video file')
                raise ValueError
            if "/" not in self.audio_text_box.text():
                ErrorDialog('Audio source error', 'You must select an audio track')
                raise ValueError
            '''Threads'''
            self.progress_bar.setValue(0)
            self.pool = QThreadPool()
            self.runnable = encoder.Encode(
                self.delay_text_box,
                self.volume_text_box,
                self.audio_ratio_text_box,
                self.audio_text_box,
                self.video_text_box,
                self.movie,
                self.output_text_box,
                self.source_video
                )
            self.runnable.signals.max_progress.connect(self.set_progress_max)
            self.runnable.signals.progress.connect(self.set_current_progress)
            self.runnable.signals.complete.connect(self.enable_encode_button)
            self.pool.start(self.runnable)
        except ValueError: self.enable_encode_button()

    def set_progress_max(self, max_progress):
        self.progress_bar.setMaximum(max_progress)

    def set_current_progress(self, current_progress):
        self.progress_bar.setValue(current_progress)

    def enable_encode_button(self):
        self.encode_button.setEnabled(True)

    def disable_encode_button(self):
        self.encode_button.setDisabled(True)

    def start_editor(self):
        self.editor = Editor(self.video_text_box.text(), self.audio_text_box.text())

    '''Executes on program end'''
    def closeEvent(self, event):
        encoder.Encode.MAIN_ALIVE = False # Kill running ffmpeg process