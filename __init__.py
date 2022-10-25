import sys

from PyQt6.QtWidgets import QApplication

import main_ui


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open(main_ui.resource_path('theme/MaterialDark.qss'), 'r') as file:
            app.setStyleSheet(file.read())
    except FileNotFoundError: pass
    ui = main_ui.Ui_MainWindow()
    sys.exit(app.exec())