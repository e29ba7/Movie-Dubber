import os

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QDialog, QProgressBar


class Directory:
    base = os.path.splitdrive(__file__)[0]
    theme = os.path.join(base, 'theme')

    @classmethod
    def data(cls, filename):
        return os.path.join(cls.theme, filename)

class DialogWindow(QDialog):
    def __init__(self, icon: str, title: str, width: int, height: int):
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self.icon = icon  # Icon sources: https://www.flaticon.com/ - created by Freepik
        self.setFixedSize(self.width, self.height)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowIcon(QIcon(Directory.data(self.icon)))
        self.setWindowTitle(self.title)
        '''Rounded border'''
        self.rounded_borders = QWidget(self)
        self.rounded_borders.setFixedSize(self.width, self.height)
        self.rounded_borders.setStyleSheet('''
            background: #1e1d23;
            border: 1px solid #444444;
            border-radius: 5px;'''
        )
        self.central_widget = QWidget(self)
        # self.central_widget.setFixedSize(self.width, self.height)
        # self.central_widget.setStyleSheet('''
        #     background: #1e1d23;'''
        # )
        '''Titlebar'''
        self.tb_icon = QLabel(self.central_widget)
        self.tb_icon.setPixmap(QPixmap(Directory.data(self.icon)))
        self.tb_icon.setGeometry(QRect(3, 4, 16, 16))
        self.tb_title = QLabel(self.central_widget)
        self.tb_title.setGeometry(QRect(25, 5, 150, 15))
        self.tb_title.setText(self.title)
        '''Close button'''
        self.close_button = QPushButton(self.central_widget)
        self.close_button.setGeometry(QRect(self.width - 21, 4, 16, 16))
        self.close_button.setText("X")
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet('''
            border: 1px solid #444444;
            border-radius: 4px;'''
        )

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        try:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()
        except AttributeError: ... # Fixes bug: Click and drag from button on program start crashes

class ErrorDialog(DialogWindow):
    def __init__(self, title, error):
        super().__init__('warning.ico', title, 300, 80)
        self.error = error
        '''Error text'''
        self.error_label = QLabel(self.central_widget)
        self.error_label.setGeometry(QRect(20, 40, 240, 15))
        self.error_label.setText(self.error)
        self.exec()

class ProgressDialog(DialogWindow):
    def __init__(self):
        super().__init__('', 'Processing...', 300, 80)
        self.progress_bar = QProgressBar(self.central_widget)
        self.progress_bar.setGeometry(QRect(20, 40, 240, 21))
        self.progress_bar.setMinimum(0)
