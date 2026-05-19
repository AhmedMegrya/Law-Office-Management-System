"""
pages/dashboard.py - Dashboard page
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QGridLayout, QTableWidget, QTableWidgetItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import database as db
from widgets import StatCard, make_table, set_table_item, AlertWidget
from styles import COLORS


class DashboardPage(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()
        self.refresh()

        # Auto-refresh every 60 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ─── Stats Row ───────────────────────────────────────────────
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(15)

        self.card_clients    = StatCard("إجمالي العملاء",       "0", "👤")
        self.card_cases      = StatCard("إجمالي القضايا",       "0", "📁")
        self.card_active     = StatCard("القضايا النشطة",        "0", "⚡", COLORS['success'])
        self.card_sessions   = StatCard("الجلسات القادمة",       "0", "📅", COLORS['warning'])
        self.card_fees       = StatCard("إجمالي الأتعاب",       "0", "💰")
        self.card_paid       = StatCard("المدفوع",               "0", "✅", COLORS['success'])
        self.card_remaining  = StatCard("المتبقي",               "0", "⏳", COLORS['danger'])

        for card in [self.card_clients, self.card_cases, self.card_active,
                     self.card_sessions, self.card_fees, self.card_paid, self.card_remaining]:
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.stats_row.addWidget(card)

        main_layout.addLayout(self.stats_row)

        # ─── Middle Row: Alerts + Recent Cases ───────────────────────
        middle = QHBoxLayout()
        middle.setSpacing(20)

        # Alerts panel
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                border-top: 3px solid {COLORS['warning']};
            }}
        """)
        alerts_layout = QVBoxLayout(alerts_frame)
        alerts_layout.setContentsMargins(15, 15, 15, 15)
        alerts_layout.setSpacing(8)

        alert_title = QLabel("⚠  تنبيهات الجلسات القريبة")
        alert_title.setStyleSheet(f"color: {COLORS['warning']}; font-size: 14px; font-weight: bold;")
        alert_title.setAlignment(Qt.AlignRight)
        alerts_layout.addWidget(alert_title)

        # Alert table
        self.alerts_table = make_table(["التاريخ", "القضية", "العميل", "المحكمة"])
        self.alerts_table.setMaximumHeight(200)
        alerts_layout.addWidget(self.alerts_table)

        # Recent cases panel
        recent_frame = QFrame()
        recent_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                border-top: 3px solid {COLORS['gold']};
            }}
        """)
        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(15, 15, 15, 15)
        recent_layout.setSpacing(8)

        recent_title = QLabel("📋  آخر القضايا المضافة")
        recent_title.setStyleSheet(f"color: {COLORS['navy']}; font-size: 14px; font-weight: bold;")
        recent_title.setAlignment(Qt.AlignRight)
        recent_layout.addWidget(recent_title)

        self.recent_table = make_table(["الحالة", "العميل", "النوع", "المحكمة", "رقم القضية", "كود"])
        self.recent_table.setMaximumHeight(200)
        recent_layout.addWidget(self.recent_table)

        middle.addWidget(recent_frame, 3)
        middle.addWidget(alerts_frame, 2)
        main_layout.addLayout(middle)

        # ─── Bottom: Today's sessions full table ─────────────────────
        today_frame = QFrame()
        today_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                border-top: 3px solid {COLORS['navy']};
            }}
        """)
        today_layout = QVBoxLayout(today_frame)
        today_layout.setContentsMargins(15, 15, 15, 15)
        today_layout.setSpacing(8)

        today_title = QLabel("📅  جلسات اليوم")
        today_title.setStyleSheet(f"color: {COLORS['navy']}; font-size: 14px; font-weight: bold;")
        today_title.setAlignment(Qt.AlignRight)
        today_layout.addWidget(today_title)

        self.today_table = make_table(["الحالة", "المطلوب", "الدائرة", "المحكمة", "الوقت", "العميل", "القضية"])
        self.today_table.setMaximumHeight(220)
        today_layout.addWidget(self.today_table)

        main_layout.addWidget(today_frame)
        main_layout.addStretch()

    def refresh(self):
        stats = db.get_dashboard_stats()

        def fmt_money(v):
            return f"{v:,.0f} ج.م"

        self.card_clients.update_value(stats["clients"])
        self.card_cases.update_value(stats["cases"])
        self.card_active.update_value(stats["active_cases"])
        self.card_sessions.update_value(stats["upcoming_sessions"])
        self.card_fees.update_value(fmt_money(stats["total_fees"]))
        self.card_paid.update_value(fmt_money(stats["total_paid"]))
        self.card_remaining.update_value(fmt_money(stats["total_remaining"]))

        # Alerts table
        alerts = stats["alerts"]
        self.alerts_table.setRowCount(len(alerts))
        for i, a in enumerate(alerts):
            set_table_item(self.alerts_table, i, 0, a.get("session_date",""))
            set_table_item(self.alerts_table, i, 1, a.get("case_code",""))
            set_table_item(self.alerts_table, i, 2, a.get("client_name",""))
            set_table_item(self.alerts_table, i, 3, a.get("court",""))

        # Recent cases table
        recent = stats["recent_cases"]
        self.recent_table.setRowCount(len(recent))
        for i, c in enumerate(recent):
            set_table_item(self.recent_table, i, 0, c.get("code",""))
            set_table_item(self.recent_table, i, 1, c.get("case_number",""))
            set_table_item(self.recent_table, i, 2, c.get("court",""))
            set_table_item(self.recent_table, i, 3, c.get("case_type",""))
            set_table_item(self.recent_table, i, 4, c.get("client_name",""))
            set_table_item(self.recent_table, i, 5, c.get("status",""),
                           color=COLORS['success'] if c.get("status") == "متداولة" else COLORS['gray_dark'])

        # Today's sessions
        today_sessions = db.get_sessions(date_filter="today")
        self.today_table.setRowCount(len(today_sessions))
        for i, s in enumerate(today_sessions):
            set_table_item(self.today_table, i, 0, s.get("case_code","") + " - " + s.get("case_number",""))
            set_table_item(self.today_table, i, 1, s.get("client_name",""))
            set_table_item(self.today_table, i, 2, s.get("session_time",""))
            set_table_item(self.today_table, i, 3, s.get("court",""))
            set_table_item(self.today_table, i, 4, s.get("circuit",""))
            set_table_item(self.today_table, i, 5, s.get("required_action",""))
            set_table_item(self.today_table, i, 6, s.get("status",""),
                           color=COLORS['warning'] if s.get("status") == "قادمة" else COLORS['success'])
