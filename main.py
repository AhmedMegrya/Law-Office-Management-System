"""
main.py - Application Entry Point
Law Office Management System
مكتب المستشار/ أحمد شعبان مجرية للمحاماة والاستشارات القانونية
"""
import sys
import os

# Fix path for PyInstaller
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    APP_DIR  = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR  = BASE_DIR

# Ensure working directory is app directory
os.chdir(APP_DIR)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QLocale, QTranslator
from PyQt5.QtGui import QFont

import database as db
from login import LoginDialog
from main_window import MainWindow
from styles import MAIN_STYLESHEET


def setup_arabic_font(app):
    """Setup Arabic-friendly font for the whole app."""
    # Try to use a good Arabic font
    for font_name in ["Segoe UI", "Arial", "Tahoma", "Sans Serif"]:
        font = QFont(font_name, 11)
        if QFont(font_name).exactMatch() or font_name in ["Segoe UI", "Arial"]:
            app.setFont(font)
            break


def start_app():
    app = QApplication.instance()
    new_app = app is None
    if new_app:
        app = QApplication(sys.argv)

    app.setApplicationName("Law Office Management System")
    app.setOrganizationName("مكتب المستشار أحمد شعبان مجرية")
    app.setLayoutDirection(Qt.RightToLeft)
    app.setStyleSheet(MAIN_STYLESHEET)
    setup_arabic_font(app)

    # Initialize database
    db.init_database()

    # Show login
    login = LoginDialog()
    if login.exec_():
        user = login.user
        if user:
            window = MainWindow(user)
            window.showMaximized()
            if new_app:
                sys.exit(app.exec_())
    else:
        if new_app:
            sys.exit(0)


if __name__ == "__main__":
    start_app()
