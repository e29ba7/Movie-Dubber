import re
import os
import sys

from PyQt6.QtCore import QRect, QRegularExpression, QThreadPool
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QProgressBar, QFileDialog, QMainWindow, QMessageBox

from database import database_ui
import encoder


# Strictly to enable including QSS StyleSheet when building with Auto-Py-to-Exe
# Source: https://dev.to/eshleron/how-to-convert-py-to-exe-step-by-step-guide-3cfi
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(271, 161)
        self.setWindowTitle("MovieDubber")
        self.setWindowIcon(QIcon(resource_path('theme/icon.ico'))) # Source: https://www.flaticon.com/free-icons/popcorn - created by pongsakornRed
        self.central_Widget = QWidget(self)
        '''Output button'''
        self.output_button = QPushButton(self.central_Widget)
        self.output_button.setGeometry(QRect(10, 10, 61, 21))
        self.output_button.setText("Open")
        self.output_button.setToolTip("<html><head/><body><p>Select file output location</p></body></html>")
        self.output_button.clicked.connect(self.output_file_location)
        '''Output text box'''
        self.output_text_box = QLineEdit(self.central_Widget)
        self.output_text_box.setGeometry(QRect(80, 10, 181, 21))
        self.output_text_box.setToolTip("<html><head/><body><p>Select file output location</p></body></html>")
        self.output_text_box.setText("Select Output Folder")
        '''Delay text box'''
        self.delay_text_box = QLineEdit(self.central_Widget)
        self.delay_text_box.setGeometry(QRect(10, 40, 101, 21))
        self.delay_text_box.setText("Delay (ms)")
        self.delay_text_box.setToolTip("<html><head/><body><p>Enter movie delay in milliseconds</p></body></html>")
        self.delay_text_box.setValidator(QRegularExpressionValidator(QRegularExpression(r'\d{6}')))
        '''Volume text box'''
        self.volume_text_box = QLineEdit(self.central_Widget)
        self.volume_text_box.setGeometry(QRect(120, 40, 61, 21))
        self.volume_text_box.setToolTip("<html><head/><body><p>Enter volume change in dB (integer). Can be negative. E.g. '5 or -3'</p></body></html>")
        self.volume_text_box.setText("Volume")
        self.volume_text_box.setValidator(QRegularExpressionValidator(QRegularExpression(r'\d{2}')))
        '''Audio ratio text box'''
        self.audio_ratio_text_box = QLineEdit(self.central_Widget)
        self.audio_ratio_text_box.setGeometry(QRect(190, 40, 71, 21))
        self.audio_ratio_text_box.setToolTip("<html><head/><body><p>Enter ratio to attenuate (While added audio is talking, the movie track will temporarily drown out.) E.g. 2.5 (Range: 1 - 20)</p></body></html>")
        self.audio_ratio_text_box.setText("Ratio")
        self.audio_ratio_text_box.setValidator(QRegularExpressionValidator(QRegularExpression(r'\d\.\d{2}')))
        '''Encode libarary dropdown'''
        # self.encode_library_dropdown = QComboBox(self.central_Widget)
        # self.encode_library_dropdown.setGeometry(QRect(10, 71, 56, 21))
        # self.encode_library_dropdown.setToolTip("<html><head/><body><p>Insert selected encoder in file name. Ex: Movie.x265.mkv</p></body></html>")
        # self.encode_library_dropdown.addItem("x265")
        # self.encode_library_dropdown.addItem("x264")
        # self.encode_library_dropdown.addItem("None")
        # self.encode_library_dropdown.setCurrentText("None")
        '''Resolution dropdown'''
        # self.resolution_dropdown = QComboBox(self.central_Widget)
        # self.resolution_dropdown.setGeometry(QRect(70, 71, 61, 21))
        # self.resolution_dropdown.setToolTip("<html><head/><body><p>Insert selected resolution in file name. Ex: Movie.1080p.mkv</p></body></html>")
        # self.resolution_dropdown.addItem("1080p")
        # self.resolution_dropdown.addItem("720p")
        # self.resolution_dropdown.addItem("480p")
        # self.resolution_dropdown.addItem("360p")
        # self.resolution_dropdown.addItem("None")
        # self.resolution_dropdown.setCurrentText("None")
        '''Bit box'''
        # self.bit_Box = QCheckBox(self.central_Widget)
        # self.bit_Box.setGeometry(QRect(135, 71, 49, 20))
        # self.bit_Box.setToolTip("<html><head/><body><p>Insert 10bit in file name. Ex: Movie.10bit.mkv</p></body></html>")
        # self.bit_Box.setText("10Bit")
        '''Video button'''
        self.video_Button = QPushButton(self.central_Widget)
        self.video_Button.setGeometry(QRect(10, 70, 61, 21))
        self.video_Button.setText("Video File")
        self.video_Button.clicked.connect(self.get_video_file)
        '''Audio button'''
        self.audio_Button = QPushButton(self.central_Widget)
        self.audio_Button.setGeometry(QRect(10, 100, 61, 21))
        self.audio_Button.setText("Audio File")
        self.audio_Button.clicked.connect(self.get_audio_file)
        '''Video text box'''
        self.video_text_box = QLineEdit(self.central_Widget)
        self.video_text_box.setGeometry(QRect(80, 71, 181, 21))
        self.video_text_box.setText('Select Video File')
        '''Audio text box'''
        self.audio_text_box = QLineEdit(self.central_Widget)
        self.audio_text_box.setGeometry(QRect(80, 100, 181, 21))
        self.audio_text_box.setText('Select Audio Track')
        '''Load button'''
        self.load_button = QPushButton(self.central_Widget)
        self.load_button.setGeometry(QRect(10, 130, 41, 21))
        self.load_button.setText("Load")
        self.load_button.setToolTip("Load sync information from database.")
        self.load_button.clicked.connect(self.open_database)
        '''Encode button'''
        self.encode_Button = QPushButton(self.central_Widget)
        self.encode_Button.setGeometry(QRect(60, 130, 61, 21))
        self.encode_Button.setText("Encode")
        self.encode_Button.clicked.connect(self.check_inputs_and_Encode)
        '''Editor button (Editor is not enabled)'''
        # self.editor_Button = QPushButton(self.central_Widget)
        # self.editor_Button.setGeometry(QRect(190, 130, 71, 21))
        # self.editor_Button.setText("Editor")
        # self.editor_Button.setToolTip("The editor isn't ready yet.")
        # self.editor_Button.setDisabled(True)
        # self.editor_Button.clicked.connect(self.start_editor)
        '''Progress bar'''
        self.progress_Bar = QProgressBar(self.central_Widget)
        self.progress_Bar.setGeometry(QRect(130, 130, 131, 21))
        self.progress_Bar.setMinimum(0)
        '''Run'''
        self.setCentralWidget(self.central_Widget)
        self.show()

    #################
    #|  FUNCTIONS  |#
    #################

    def error_message(self, title, text):
        self.error = QMessageBox(parent=self, text=text)
        self.error.setWindowTitle(title)
        self.error.exec()

    def get_video_file(self):
        self.video_file = QFileDialog.getOpenFileName(parent=self, caption='Select Video File', filter='Video files (*.mkv *.mp4 *.avi *.mov )')
        self.video_text_box.setText(self.video_file[0])

    def get_audio_file(self):
        self.audio_file = QFileDialog.getOpenFileName(parent=self, caption='Select Audio File', filter='Audio files (*.mp3 *.m4a)')
        self.audio_text_box.setText(self.audio_file[0])

    def output_file_location(self):
        self.save_loc = QFileDialog.getExistingDirectory(parent=self, caption='Select save location')
        self.output_text_box.setText(self.save_loc)

    def open_database(self):
        try:
            self.data = database_ui.Ui_Database().data
            self.movie = self.data[0]
            self.delay_text_box.setText(str(self.data[3]))
            self.audio_ratio_text_box.setText(str(self.data[4]))
            self.volume_text_box.setText(str(self.data[5]))
        except (IndexError): ...

    def check_inputs_and_Encode(self):
        try:
            '''Check Delay, Volume, and Ratio text boxes'''
            if "/" not in self.output_text_box.text():
                self.error_message('Output location error', 'You must select an output location folder.')
                raise Exception
            if not re.match(r'\d', self.delay_text_box.text()):
                self.error_message('Delay error', 'You must provide a delay in milliseconds')
                raise Exception
            if not re.match(r'\d', self.volume_text_box.text()):
                self.volume_text_box.setText('0')
            if not re.match(r'\d', self.audio_ratio_text_box.text()):
                self.audio_ratio_text_box.setText('1')
            if "/" in self.video_text_box.text():
                self.source_video = re.split("/", self.video_text_box.text())[-1]
            else:
                self.error_message('Video source error', 'You must select a video file')
                raise Exception
            if "/" not in self.audio_text_box.text():
                self.error_message('Audio source error', 'You must select an audio track')
                raise Exception

            self.progress_Bar.setValue(0)
            self.pool = QThreadPool()
            self.runnable = encoder.Encode(self.delay_text_box, self.volume_text_box, self.audio_ratio_text_box, self.audio_text_box, self.video_text_box, self.movie, self.output_text_box, self.source_video)
            self.runnable.signals.max_progress.connect(self.set_progress_max)
            self.runnable.signals.max_progress.connect(self.disable_encode_button)
            self.runnable.signals.progress.connect(self.set_current_progress)
            self.runnable.signals.complete.connect(self.enable_encode_button)
            self.pool.start(self.runnable)
        except Exception: ...

    def set_progress_max(self, max_progress):
        self.progress_Bar.setMaximum(max_progress)

    def set_current_progress(self, current_progress):
        self.progress_Bar.setValue(current_progress)

    def enable_encode_button(self, true):
        self.encode_Button.setEnabled(true)

    def disable_encode_button(self):
        self.encode_Button.setDisabled(True)

    '''Executes on program end'''
    def closeEvent(self, event):
        encoder.Encode.MAIN_ALIVE = False