import pathlib

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QSlider, QWidget


class Directory:
    base = pathlib.Path(__file__).parents[0]
    theme_dir = base / 'theme'

    @classmethod
    def theme(cls, filename: str) -> str:
        return str(cls.theme_dir / filename)


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
        self.setWindowIcon(QIcon(Directory.theme(self.icon)))
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
        '''Titlebar'''
        self.tb_icon = QLabel(self.central_widget)
        self.tb_icon.setPixmap(QPixmap(Directory.theme(self.icon)))
        self.tb_icon.setGeometry(QRect(3, 4, 16, 16))
        self.tb_title = QLabel(self.title, self.central_widget)
        self.tb_title.setGeometry(QRect(25, 5, 150, 15))
        '''Close button'''
        self.close_button = Button('X', self.central_widget)
        self.close_button.setGeometry(QRect(self.width - 20, 4, 16, 16))
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet('''
            border: 1px solid #444444;
            border-radius: 4px;'''
            )

    def mousePressEvent(self, mouse_event):
        self.drag_position = mouse_event.globalPosition().toPoint()

    def mouseMoveEvent(self, mouse_event):
        try:
            self.move(self.pos() + mouse_event.globalPosition().toPoint() - self.drag_position)
            self.drag_position = mouse_event.globalPosition().toPoint()
            mouse_event.accept()
        except AttributeError: ...


class ErrorDialog(DialogWindow):
    def __init__(self, title: str, error: str):
        super().__init__('warning.ico', title, 300, 80)
        self.error = error
        '''Error text'''
        self.error_label = QLabel(self.central_widget)
        self.error_label.setGeometry(QRect(20, 40, 240, 15))
        self.error_label.setText(self.error)
        self.exec()


class Button(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)

    #Ignore click and drag
    def mouseMoveEvent(self, mouse_event):
        ...


class Slider(QSlider):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)

    def mouseMoveEvent(self, mouse_event):
        ...
