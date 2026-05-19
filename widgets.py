"""
widgets.py - Reusable UI components for Law Office Management System
"""
from PyQt5.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit,
    QHBoxLayout, QVBoxLayout, QFrame, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QSizePolicy,
    QTextEdit, QSpinBox, QMessageBox, QDialog, QDialogButtonBox,
    QScrollArea
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QFont, QIcon, QColor
from styles import COLORS


def make_btn(text, btn_type="primary", parent=None):
    """Create a styled button."""
    btn = QPushButton(text, parent)
    btn.setObjectName(f"btn_{btn_type}")
    btn.setCursor(Qt.PointingHandCursor)
    return btn


def make_label(text, label_type="normal", parent=None):
    """Create a styled label."""
    lbl = QLabel(text, parent)
    if label_type == "section":
        lbl.setObjectName("section_title")
    elif label_type == "form":
        lbl.setObjectName("form_label")
    lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    return lbl


def make_input(placeholder="", parent=None):
    """Create a styled QLineEdit."""
    inp = QLineEdit(parent)
    inp.setPlaceholderText(placeholder)
    inp.setLayoutDirection(Qt.RightToLeft)
    inp.setAlignment(Qt.AlignRight)
    return inp


def make_combo(items, parent=None):
    """Create a styled QComboBox."""
    cb = QComboBox(parent)
    cb.addItems(items)
    cb.setLayoutDirection(Qt.RightToLeft)
    return cb


def make_date(parent=None):
    """Create a styled QDateEdit."""
    de = QDateEdit(parent)
    de.setDate(QDate.currentDate())
    de.setCalendarPopup(True)
    de.setDisplayFormat("yyyy-MM-dd")
    de.setLayoutDirection(Qt.RightToLeft)
    return de


def make_textarea(parent=None, rows=3):
    """Create a styled QTextEdit."""
    te = QTextEdit(parent)
    te.setLayoutDirection(Qt.RightToLeft)
    te.setFixedHeight(rows * 25 + 10)
    return te


def make_separator():
    """Create a horizontal separator line."""
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setObjectName("separator")
    return sep


def make_table(headers, parent=None):
    """Create a styled table with given headers (RTL)."""
    tbl = QTableWidget(parent)
    tbl.setColumnCount(len(headers))
    tbl.setHorizontalHeaderLabels(headers)
    tbl.setLayoutDirection(Qt.RightToLeft)
    tbl.setAlternatingRowColors(True)
    tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
    tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tbl.setSelectionMode(QAbstractItemView.SingleSelection)
    tbl.verticalHeader().setVisible(False)
    tbl.horizontalHeader().setStretchLastSection(True)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    tbl.setShowGrid(True)
    tbl.setSortingEnabled(True)
    tbl.setWordWrap(False)
    tbl.setAlternatingRowColors(True)
    return tbl


def set_table_item(table, row, col, text, color=None, align=Qt.AlignRight | Qt.AlignVCenter):
    """Set a table item with alignment."""
    item = QTableWidgetItem(str(text) if text is not None else "")
    item.setTextAlignment(align)
    if color:
        item.setForeground(QColor(color))
    table.setItem(row, col, item)


def confirm_delete(parent=None, msg="هل تريد حذف هذا العنصر؟"):
    """Show delete confirmation dialog."""
    reply = QMessageBox.question(
        parent, "تأكيد الحذف", msg,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return reply == QMessageBox.Yes


def show_info(parent, title, msg):
    QMessageBox.information(parent, title, msg)


def show_error(parent, title, msg):
    QMessageBox.critical(parent, title, msg)


def show_warning(parent, title, msg):
    QMessageBox.warning(parent, title, msg)


class StatCard(QFrame):
    """A dashboard statistic card widget."""
    def __init__(self, title, value, icon="", color=None, parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.setFixedHeight(110)
        self.setMinimumWidth(150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(5)

        # Top row: icon + value
        top = QHBoxLayout()
        val_lbl = QLabel(str(value))
        val_lbl.setObjectName("stat_number")
        val_font = QFont()
        val_font.setPointSize(22)
        val_font.setBold(True)
        val_lbl.setFont(val_font)
        if color:
            val_lbl.setStyleSheet(f"color: {color};")
        val_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 24px; color: {COLORS['gold']};")
        icon_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        top.addWidget(val_lbl)
        top.addStretch()
        top.addWidget(icon_lbl)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setObjectName("stat_label")
        title_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addLayout(top)
        layout.addWidget(title_lbl)
        self.val_lbl = val_lbl

    def update_value(self, value):
        self.val_lbl.setText(str(value))


class SectionHeader(QWidget):
    """A page section header with title and toolbar."""
    def __init__(self, title, buttons=None, parent=None):
        super().__init__(parent)
        self.setObjectName("toolbar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Title on the right (RTL)
        title_lbl = make_label(title, "section")
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_lbl.setFont(title_font)

        layout.addStretch()
        layout.addWidget(title_lbl)

        # Buttons on the left
        if buttons:
            for btn in buttons:
                layout.insertWidget(0, btn)


class FormRow(QHBoxLayout):
    """A right-to-left form field row: label + widget."""
    def __init__(self, label_text, widget, required=False):
        super().__init__()
        self.setContentsMargins(0, 2, 0, 2)
        self.setSpacing(10)

        lbl_text = f"* {label_text}" if required else label_text
        lbl = make_label(lbl_text, "form")
        lbl.setFixedWidth(140)
        if required:
            lbl.setStyleSheet(f"color: {COLORS['gold_dark']}; font-weight: bold;")

        self.addWidget(widget)
        self.addWidget(lbl)


class AlertWidget(QFrame):
    """Small alert/notification widget."""
    def __init__(self, text, alert_type="warning", parent=None):
        super().__init__(parent)
        self.setObjectName("alert_box")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        icons = {"warning": "⚠", "info": "ℹ", "success": "✓", "danger": "✗"}
        icon_lbl = QLabel(icons.get(alert_type, "•"))
        icon_lbl.setStyleSheet(f"font-size: 16px; color: {COLORS['warning']};")

        text_lbl = QLabel(text)
        text_lbl.setLayoutDirection(Qt.RightToLeft)
        text_lbl.setWordWrap(True)

        layout.addWidget(text_lbl)
        layout.addStretch()
        layout.addWidget(icon_lbl)
