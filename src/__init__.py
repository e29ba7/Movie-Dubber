import sys

from PyQt6.QtWidgets import QApplication

from utils import Directory
import main_ui as main_ui


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open(Directory.data('MaterialDark.qss'), 'r') as file:
            app.setStyleSheet(file.read())
    except FileNotFoundError: ...
    ui = main_ui.MainWindow()
    sys.exit(app.exec())