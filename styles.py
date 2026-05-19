"""
styles.py - Color palette and stylesheet for Law Office Management System
Arabic RTL, Gold/Navy/White luxury theme
"""

# Color Palette
COLORS = {
    "navy":       "#0D1B3E",
    "navy_light": "#1A2F5E",
    "navy_mid":   "#162447",
    "gold":       "#C9A84C",
    "gold_light": "#E8C97A",
    "gold_dark":  "#A0742A",
    "white":      "#FFFFFF",
    "off_white":  "#F5F3EE",
    "gray_light": "#E8E6E0",
    "gray_mid":   "#B0A898",
    "gray_dark":  "#6B6155",
    "bg_main":    "#F0EDE6",
    "bg_card":    "#FFFFFF",
    "text_dark":  "#1A1208",
    "text_mid":   "#4A3F30",
    "success":    "#2D7A3A",
    "danger":     "#8B1A1A",
    "warning":    "#B8860B",
    "sidebar_bg": "#0D1B3E",
    "sidebar_hover": "#1A2F5E",
    "sidebar_active": "#C9A84C",
    "header_bg":  "#0D1B3E",
    "table_header": "#0D1B3E",
    "table_row_odd": "#FFFFFF",
    "table_row_even": "#F5F3EE",
    "table_selected": "#FFF8E7",
    "border":     "#D4C5A0",
    "input_bg":   "#FAFAF7",
    "btn_primary": "#C9A84C",
    "btn_primary_hover": "#E8C97A",
    "btn_danger":  "#8B1A1A",
    "btn_success": "#2D7A3A",
}

MAIN_STYLESHEET = f"""
/* ─── Global ─── */
QMainWindow, QDialog, QWidget {{
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_dark']};
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}}

/* ─── Sidebar ─── */
#sidebar {{
    background-color: {COLORS['sidebar_bg']};
    border-right: 2px solid {COLORS['gold_dark']};
    min-width: 220px;
    max-width: 220px;
}}

#sidebar_header {{
    background-color: {COLORS['navy_mid']};
    padding: 20px 10px;
    border-bottom: 2px solid {COLORS['gold']};
}}

#office_name_label {{
    color: {COLORS['gold']};
    font-size: 13px;
    font-weight: bold;
    text-align: center;
}}

#office_sub_label {{
    color: {COLORS['gray_mid']};
    font-size: 11px;
    text-align: center;
}}

QPushButton#nav_btn {{
    background-color: transparent;
    color: {COLORS['off_white']};
    border: none;
    text-align: right;
    padding: 12px 16px;
    font-size: 13px;
    font-weight: normal;
    border-left: 3px solid transparent;
}}

QPushButton#nav_btn:hover {{
    background-color: {COLORS['sidebar_hover']};
    color: {COLORS['gold_light']};
}}

QPushButton#nav_btn:checked {{
    background-color: {COLORS['sidebar_hover']};
    color: {COLORS['gold']};
    border-left: 3px solid {COLORS['gold']};
    font-weight: bold;
}}

/* ─── Header ─── */
#header_bar {{
    background-color: {COLORS['header_bg']};
    min-height: 60px;
    max-height: 60px;
    border-bottom: 2px solid {COLORS['gold']};
}}

#page_title_label {{
    color: {COLORS['gold']};
    font-size: 18px;
    font-weight: bold;
}}

#search_global {{
    background-color: {COLORS['navy_light']};
    color: {COLORS['white']};
    border: 1px solid {COLORS['gold_dark']};
    border-radius: 20px;
    padding: 6px 15px;
    font-size: 13px;
    min-width: 250px;
}}

#search_global::placeholder {{
    color: {COLORS['gray_mid']};
}}

#user_label {{
    color: {COLORS['gold_light']};
    font-size: 12px;
}}

/* ─── Content Area ─── */
#content_area {{
    background-color: {COLORS['bg_main']};
    padding: 0px;
}}

/* ─── Dashboard Cards ─── */
#stat_card {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    border-top: 3px solid {COLORS['gold']};
}}

#stat_number {{
    color: {COLORS['navy']};
    font-size: 28px;
    font-weight: bold;
}}

#stat_label {{
    color: {COLORS['gray_dark']};
    font-size: 12px;
}}

/* ─── Tables ─── */
QTableWidget {{
    background-color: {COLORS['white']};
    gridline-color: {COLORS['gray_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    selection-background-color: {COLORS['table_selected']};
    selection-color: {COLORS['text_dark']};
    font-size: 13px;
}}

QTableWidget::item {{
    padding: 8px 10px;
    border-bottom: 1px solid {COLORS['gray_light']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS['table_selected']};
    color: {COLORS['text_dark']};
}}

QHeaderView::section {{
    background-color: {COLORS['table_header']};
    color: {COLORS['gold']};
    padding: 10px;
    border: none;
    font-weight: bold;
    font-size: 13px;
}}

/* ─── Buttons ─── */
QPushButton#btn_primary {{
    background-color: {COLORS['gold']};
    color: {COLORS['navy']};
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 13px;
    min-width: 100px;
}}

QPushButton#btn_primary:hover {{
    background-color: {COLORS['gold_light']};
}}

QPushButton#btn_primary:pressed {{
    background-color: {COLORS['gold_dark']};
}}

QPushButton#btn_danger {{
    background-color: {COLORS['danger']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 13px;
}}

QPushButton#btn_danger:hover {{
    background-color: #A02020;
}}

QPushButton#btn_success {{
    background-color: {COLORS['success']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 13px;
}}

QPushButton#btn_success:hover {{
    background-color: #3A9A48;
}}

QPushButton#btn_secondary {{
    background-color: {COLORS['gray_light']};
    color: {COLORS['text_dark']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
}}

QPushButton#btn_secondary:hover {{
    background-color: {COLORS['gray_mid']};
}}

/* ─── Inputs ─── */
QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox {{
    background-color: {COLORS['input_bg']};
    border: 1px solid {COLORS['border']};
    border-radius: 5px;
    padding: 7px 10px;
    font-size: 13px;
    color: {COLORS['text_dark']};
    selection-background-color: {COLORS['gold_light']};
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
    border: 2px solid {COLORS['gold']};
    background-color: {COLORS['white']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['gold_light']};
}}

/* ─── Labels ─── */
QLabel#section_title {{
    color: {COLORS['navy']};
    font-size: 16px;
    font-weight: bold;
    border-bottom: 2px solid {COLORS['gold']};
    padding-bottom: 5px;
}}

QLabel#form_label {{
    color: {COLORS['text_mid']};
    font-size: 13px;
    font-weight: bold;
}}

/* ─── GroupBox ─── */
QGroupBox {{
    font-weight: bold;
    color: {COLORS['navy']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    margin-top: 12px;
    padding: 15px;
    background-color: {COLORS['white']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top right;
    padding: 0 10px;
    background-color: {COLORS['white']};
    color: {COLORS['gold_dark']};
    font-size: 14px;
    font-weight: bold;
}}

/* ─── ScrollBar ─── */
QScrollBar:vertical {{
    background: {COLORS['gray_light']};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['gold_dark']};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['gold']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {COLORS['gray_light']};
    height: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['gold_dark']};
    border-radius: 5px;
}}

/* ─── Tab Widget ─── */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['white']};
}}

QTabBar::tab {{
    background-color: {COLORS['gray_light']};
    color: {COLORS['text_mid']};
    padding: 8px 20px;
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    border-radius: 4px 4px 0 0;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['navy']};
    color: {COLORS['gold']};
    font-weight: bold;
}}

QTabBar::tab:hover {{
    background-color: {COLORS['navy_light']};
    color: {COLORS['gold_light']};
}}

/* ─── MessageBox ─── */
QMessageBox {{
    background-color: {COLORS['white']};
}}

/* ─── Separator ─── */
QFrame#separator {{
    background-color: {COLORS['border']};
    max-height: 1px;
    min-height: 1px;
}}

/* ─── Status Badge ─── */
QLabel#badge_active {{
    background-color: #E8F5E9;
    color: {COLORS['success']};
    border: 1px solid {COLORS['success']};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}}

QLabel#badge_closed {{
    background-color: #FFEBEE;
    color: {COLORS['danger']};
    border: 1px solid {COLORS['danger']};
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}}

/* ─── Alert Box ─── */
#alert_box {{
    background-color: #FFF8E1;
    border: 1px solid {COLORS['warning']};
    border-radius: 6px;
    padding: 10px;
}}

/* ─── Toolbar ─── */
#toolbar {{
    background-color: {COLORS['white']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 8px 15px;
}}
"""
