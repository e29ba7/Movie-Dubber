import sys

from PyQt6.QtWidgets import QApplication

import main_ui as main_ui
from utils import Directory

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open(Directory.data('MaterialDark.qss'), 'r') as file:
            app.setStyleSheet(file.read())
    except FileNotFoundError: ...
    ui = main_ui.MainWindow()
    sys.exit(app.exec())