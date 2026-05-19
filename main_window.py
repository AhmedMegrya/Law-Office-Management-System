"""
main_window.py - Main Application Window
Law Office Management System
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStackedWidget, QLineEdit, QListWidget,
    QListWidgetItem, QApplication, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor
from datetime import datetime

from styles import COLORS, MAIN_STYLESHEET
import database as db

from pages.dashboard import DashboardPage
from pages.clients import ClientsPage
from pages.cases import CasesPage
from pages.sessions import SessionsPage
from pages.fees import FeesPage, ExpensesPage
from pages.archive import ArchivePage
from pages.poa import POAPage
from pages.reports import ReportsPage
from pages.settings import SettingsPage


NAV_ITEMS = [
    ("🏠", "لوحة التحكم",   "dashboard"),
    ("👤", "العملاء",       "clients"),
    ("📁", "القضايا",       "cases"),
    ("📅", "الجلسات",       "sessions"),
    ("💰", "الأتعاب",       "fees"),
    ("📊", "المصروفات",     "expenses"),
    ("🗂", "الأرشيف",       "archive"),
    ("📜", "التوكيلات",     "poa"),
    ("📋", "التقارير",      "reports"),
    ("⚙",  "الإعدادات",    "settings"),
]


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("نظام إدارة مكتب المحاماة - " + db.get_setting("office_name"))
        self.setMinimumSize(1200, 750)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet(MAIN_STYLESHEET)

        self._pages = {}
        self._nav_buttons = {}
        self._build_ui()
        self._navigate("dashboard")

        # Clock update
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

    # ─── UI Builder ──────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # Right panel (header + content)
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(0)

        header = self._build_header()
        right_panel.addWidget(header)

        # Content area
        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")
        right_panel.addWidget(self.stack)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        root.addWidget(right_widget, 1)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Office header
        header = QFrame()
        header.setObjectName("sidebar_header")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(15, 20, 15, 20)
        h_layout.setSpacing(6)
        h_layout.setAlignment(Qt.AlignCenter)

        logo_lbl = QLabel("⚖")
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setStyleSheet(f"font-size: 36px; color: {COLORS['gold']}; background: transparent;")

        office_name = db.get_setting("office_name", "مكتب المستشار/ أحمد شعبان مجرية")
        name_lbl = QLabel(office_name)
        name_lbl.setObjectName("office_name_label")
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet(f"color: {COLORS['gold']}; font-size: 12px; font-weight: bold; background: transparent;")

        sub_lbl = QLabel("للمحاماة والاستشارات القانونية")
        sub_lbl.setObjectName("office_sub_label")
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setStyleSheet(f"color: {COLORS['gray_mid']}; font-size: 10px; background: transparent;")

        h_layout.addWidget(logo_lbl)
        h_layout.addWidget(name_lbl)
        h_layout.addWidget(sub_lbl)
        layout.addWidget(header)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {COLORS['gold_dark']};")
        layout.addWidget(div)

        # Navigation buttons
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 8, 0, 8)
        nav_layout.setSpacing(2)

        for icon, label, page_key in NAV_ITEMS:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setLayoutDirection(Qt.RightToLeft)
            btn.setFixedHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
            font = QFont()
            font.setPointSize(12)
            btn.setFont(font)
            btn.clicked.connect(lambda _, k=page_key: self._navigate(k))
            self._nav_buttons[page_key] = btn
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        layout.addWidget(nav_container, 1)

        # Bottom: user info + logout
        bottom = QFrame()
        bottom.setStyleSheet(f"background: {COLORS['navy_mid']}; border-top: 1px solid {COLORS['gold_dark']};")
        bot_layout = QVBoxLayout(bottom)
        bot_layout.setContentsMargins(12, 10, 12, 10)
        bot_layout.setSpacing(4)

        role_names = {"admin": "مدير", "employee": "موظف", "viewer": "مشاهدة"}
        role_display = role_names.get(self.user.get("role",""), self.user.get("role",""))

        user_lbl = QLabel(f"👤  {self.user.get('full_name', self.user.get('username'))}")
        user_lbl.setStyleSheet(f"color: {COLORS['gold_light']}; font-size: 12px; font-weight: bold;")
        user_lbl.setAlignment(Qt.AlignRight)

        role_lbl = QLabel(f"الصلاحية: {role_display}")
        role_lbl.setStyleSheet(f"color: {COLORS['gray_mid']}; font-size: 11px;")
        role_lbl.setAlignment(Qt.AlignRight)

        logout_btn = QPushButton("🚪  تسجيل الخروج")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['gray_mid']};
                border: 1px solid {COLORS['gray_dark']};
                border-radius: 4px;
                padding: 5px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {COLORS['danger']};
                color: white;
                border-color: {COLORS['danger']};
            }}
        """)
        logout_btn.clicked.connect(self._logout)

        bot_layout.addWidget(user_lbl)
        bot_layout.addWidget(role_lbl)
        bot_layout.addWidget(logout_btn)
        layout.addWidget(bottom)

        return sidebar

    def _build_header(self):
        header = QFrame()
        header.setObjectName("header_bar")
        header.setFixedHeight(58)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(15)

        self.page_title = QLabel("لوحة التحكم")
        self.page_title.setObjectName("page_title_label")
        fnt = QFont(); fnt.setPointSize(16); fnt.setBold(True)
        self.page_title.setFont(fnt)

        # Global search
        self.global_search = QLineEdit()
        self.global_search.setObjectName("search_global")
        self.global_search.setPlaceholderText("🔍  بحث شامل في النظام...")
        self.global_search.setLayoutDirection(Qt.RightToLeft)
        self.global_search.setFixedWidth(300)
        self.global_search.returnPressed.connect(self._global_search)

        self.clock_lbl = QLabel("")
        self.clock_lbl.setStyleSheet(f"color: {COLORS['gold_light']}; font-size: 12px;")

        layout.addWidget(self.page_title)
        layout.addStretch()
        layout.addWidget(self.global_search)
        layout.addWidget(self.clock_lbl)

        return header

    # ─── Navigation ──────────────────────────────────────────────────
    def _navigate(self, page_key):
        # Update nav button states
        for key, btn in self._nav_buttons.items():
            btn.setChecked(key == page_key)

        # Build page if not cached
        if page_key not in self._pages:
            page = self._build_page(page_key)
            if page:
                self._pages[page_key] = page
                self.stack.addWidget(page)

        if page_key in self._pages:
            self.stack.setCurrentWidget(self._pages[page_key])

        # Update header title
        titles = {k: label for _, label, k in NAV_ITEMS}
        self.page_title.setText(titles.get(page_key, ""))

    def _build_page(self, key):
        pages = {
            "dashboard": lambda: DashboardPage(self.user),
            "clients":   lambda: ClientsPage(self.user),
            "cases":     lambda: CasesPage(self.user),
            "sessions":  lambda: SessionsPage(self.user),
            "fees":      lambda: FeesPage(self.user),
            "expenses":  lambda: ExpensesPage(self.user),
            "archive":   lambda: ArchivePage(self.user),
            "poa":       lambda: POAPage(self.user),
            "reports":   lambda: ReportsPage(self.user),
            "settings":  lambda: SettingsPage(self.user),
        }
        factory = pages.get(key)
        return factory() if factory else None

    # ─── Global Search ───────────────────────────────────────────────
    def _global_search(self):
        query = self.global_search.text().strip()
        if not query:
            return
        results = db.global_search(query)
        if not results:
            from widgets import show_info
            show_info(self, "البحث", f"لم يتم العثور على نتائج لـ: {query}")
            return

        # Show results in dialog
        dlg = SearchResultsDialog(query, results, self)
        dlg.navigate_signal.connect(self._navigate)
        dlg.exec_()

    def _update_clock(self):
        now = datetime.now()
        days_ar = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
        day_name = days_ar[now.weekday()]
        self.clock_lbl.setText(f"{day_name}  {now.strftime('%Y-%m-%d  %H:%M:%S')}")

    def _logout(self):
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "تسجيل الخروج", "هل تريد تسجيل الخروج؟",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()
            from login import LoginDialog
            from main import start_app
            start_app()


from PyQt5.QtCore import pyqtSignal


class SearchResultsDialog(QWidget):
    navigate_signal = pyqtSignal(str)

    def __init__(self, query, results, parent=None):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
        # Use QDialog
        self._dialog = _SearchDialog(query, results, parent)

    def exec_(self):
        self._dialog.exec_()


class _SearchDialog:
    def __init__(self, query, results, parent):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget
        from widgets import make_table, set_table_item

        self.dlg = QDialog(parent)
        self.dlg.setWindowTitle(f"نتائج البحث: {query}")
        self.dlg.setMinimumSize(600, 400)
        self.dlg.setLayoutDirection(Qt.RightToLeft)

        layout = QVBoxLayout(self.dlg)
        lbl = QLabel(f"نتائج البحث عن: '{query}' - وُجد {len(results)} نتيجة")
        lbl.setObjectName("section_title")
        lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(lbl)

        tbl = make_table(["النوع", "العنوان", "التفاصيل"])
        tbl.setRowCount(len(results))

        type_names = {"client": "عميل", "case": "قضية", "poa": "توكيل"}
        for i, r in enumerate(results):
            set_table_item(tbl, i, 0, r.get("title",""))
            set_table_item(tbl, i, 1, r.get("detail",""))
            set_table_item(tbl, i, 2, type_names.get(r.get("type",""), r.get("type","")))

        layout.addWidget(tbl)

        from widgets import make_btn
        close_btn = make_btn("إغلاق", "secondary")
        close_btn.clicked.connect(self.dlg.reject)
        layout.addWidget(close_btn, alignment=Qt.AlignLeft)

    def exec_(self):
        self.dlg.exec_()
