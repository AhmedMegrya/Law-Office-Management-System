"""
login.py - Login dialog for Law Office Management System
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QWidget, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor
import database as db
from styles import COLORS, MAIN_STYLESHEET


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.user = None
        self.setWindowTitle("تسجيل الدخول - نظام إدارة مكتب المحاماة")
        self.setFixedSize(480, 500)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(MAIN_STYLESHEET)
        self._build_ui()
        self._center()

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _build_ui(self):
        # Outer container with rounded corners and shadow
        outer = QFrame(self)
        outer.setGeometry(0, 0, 480, 500)
        outer.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 15px;
                border: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(outer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header banner
        header = QFrame()
        header.setFixedHeight(170)
        header.setStyleSheet(f"""
            background-color: {COLORS['navy']};
            border-radius: 15px 15px 0 0;
            border-bottom: 3px solid {COLORS['gold']};
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(5)

        # Logo / icon
        logo_lbl = QLabel("⚖")
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setStyleSheet(f"font-size: 48px; color: {COLORS['gold']}; background: transparent;")

        office_lbl = QLabel(db.get_setting("office_name", "مكتب المستشار/ أحمد شعبان مجرية"))
        office_lbl.setAlignment(Qt.AlignCenter)
        office_lbl.setStyleSheet(f"color: {COLORS['gold']}; font-size: 14px; font-weight: bold; background: transparent;")
        office_lbl.setWordWrap(True)

        sub_lbl = QLabel(db.get_setting("office_subtitle", "للمحاماة والاستشارات القانونية"))
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setStyleSheet(f"color: {COLORS['gray_mid']}; font-size: 12px; background: transparent;")

        header_layout.addWidget(logo_lbl)
        header_layout.addWidget(office_lbl)
        header_layout.addWidget(sub_lbl)
        layout.addWidget(header)

        # Form area
        form_widget = QWidget()
        form_widget.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(50, 30, 50, 30)
        form_layout.setSpacing(15)

        title = QLabel("تسجيل الدخول")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['navy']}; font-size: 18px; font-weight: bold;")
        form_layout.addWidget(title)
        form_layout.addSpacing(10)

        # Username
        user_lbl = QLabel("اسم المستخدم")
        user_lbl.setAlignment(Qt.AlignRight)
        user_lbl.setStyleSheet(f"color: {COLORS['text_mid']}; font-weight: bold; font-size: 13px;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("أدخل اسم المستخدم")
        self.username_input.setAlignment(Qt.AlignRight)
        self.username_input.setLayoutDirection(Qt.RightToLeft)
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                background: {COLORS['off_white']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['gold']};
                background: white;
            }}
        """)
        self.username_input.setFixedHeight(44)

        # Password
        pass_lbl = QLabel("كلمة المرور")
        pass_lbl.setAlignment(Qt.AlignRight)
        pass_lbl.setStyleSheet(f"color: {COLORS['text_mid']}; font-weight: bold; font-size: 13px;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("أدخل كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setAlignment(Qt.AlignRight)
        self.password_input.setLayoutDirection(Qt.RightToLeft)
        self.password_input.setStyleSheet(self.username_input.styleSheet())
        self.password_input.setFixedHeight(44)
        self.password_input.returnPressed.connect(self._do_login)

        # Error label
        self.error_lbl = QLabel("")
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.setStyleSheet(f"color: {COLORS['danger']}; font-size: 12px;")

        # Login button
        login_btn = QPushButton("دخول")
        login_btn.setFixedHeight(46)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['gold']};
                color: {COLORS['navy']};
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['gold_light']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['gold_dark']};
            }}
        """)
        login_btn.clicked.connect(self._do_login)

        form_layout.addWidget(user_lbl)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(pass_lbl)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.error_lbl)
        form_layout.addSpacing(5)
        form_layout.addWidget(login_btn)
        form_layout.addStretch()

        # Footer
        footer = QLabel("Law Office Management System v1.0")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {COLORS['gray_mid']}; font-size: 10px; padding: 10px;")

        layout.addWidget(form_widget)
        layout.addWidget(footer)

        self.username_input.setFocus()

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            self.error_lbl.setText("الرجاء إدخال اسم المستخدم وكلمة المرور")
            return
        user = db.authenticate_user(username, password)
        if user:
            self.user = user
            self.accept()
        else:
            self.error_lbl.setText("اسم المستخدم أو كلمة المرور غير صحيحة")
            self.password_input.clear()
            self.password_input.setFocus()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
