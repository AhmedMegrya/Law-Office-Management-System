"""
pages/cases.py - Cases Management Page
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialog, QFormLayout, QComboBox, QTextEdit,
    QTableWidget, QFrame, QDateEdit, QSplitter, QApplication
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import subprocess, sys, os
import database as db
from widgets import (
    make_btn, make_label, make_input, make_combo, make_textarea,
    make_table, set_table_item, confirm_delete, show_info, show_error,
    make_date
)
from styles import COLORS


CASE_TYPES = ["مدني", "جنائي", "أسرة", "تجاري", "إداري", "عمالي", "إيجارات", "أخرى"]
CASE_STATUSES = ["متداولة", "محجوزة للحكم", "منتهية", "مؤجلة", "مشطوبة", "أخرى"]
CLIENT_ROLES = ["مدعي", "مدعى عليه", "متهم", "مجني عليه", "مستأنف", "مستأنف ضده"]


class CaseDialog(QDialog):
    def __init__(self, parent=None, case_data=None):
        super().__init__(parent)
        self.case_data = case_data
        self.setWindowTitle("إضافة قضية" if not case_data else "تعديل بيانات القضية")
        self.setMinimumWidth(620)
        self.setMinimumHeight(650)
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()
        if case_data:
            self._populate(case_data)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("بيانات القضية")
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # ─── Client Selection ────────────────────────────────────────
        client_row = QHBoxLayout()
        client_lbl = QLabel("* العميل:")
        client_lbl.setObjectName("form_label")
        client_lbl.setFixedWidth(130)

        self.client_search = make_input("ابحث عن العميل بالاسم...")
        self.client_search.textChanged.connect(self._filter_clients)

        self.client_combo = QComboBox()
        self.client_combo.setLayoutDirection(Qt.RightToLeft)
        self.client_combo.setMinimumWidth(200)
        self._load_clients()

        client_row.addWidget(self.client_combo)
        client_row.addWidget(self.client_search)
        client_row.addWidget(client_lbl)
        layout.addLayout(client_row)

        # ─── Form Grid ───────────────────────────────────────────────
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        self.f_client_role = make_combo(CLIENT_ROLES)
        self.f_case_type   = make_combo(CASE_TYPES)
        self.f_case_number = make_input("رقم القضية")
        self.f_case_year   = make_input("سنة القضية")
        self.f_court       = make_input("اسم المحكمة")
        self.f_circuit     = make_input("رقم/اسم الدائرة")
        self.f_opponent    = make_input("اسم الخصم")
        self.f_opp_lawyer  = make_input("محامي الخصم")
        self.f_subject     = make_textarea(rows=2)
        self.f_requests    = make_textarea(rows=2)
        self.f_last_action = make_textarea(rows=2)
        self.f_status      = make_combo(CASE_STATUSES)
        self.f_open_date   = make_date()
        self.f_notes       = make_textarea(rows=3)

        fields = [
            ("* صفة العميل:", self.f_client_role),
            ("* نوع القضية:", self.f_case_type),
            ("رقم القضية:", self.f_case_number),
            ("سنة القضية:", self.f_case_year),
            ("المحكمة:", self.f_court),
            ("الدائرة:", self.f_circuit),
            ("الخصم:", self.f_opponent),
            ("محامي الخصم:", self.f_opp_lawyer),
            ("موضوع القضية:", self.f_subject),
            ("الطلبات:", self.f_requests),
            ("آخر إجراء:", self.f_last_action),
            ("* حالة القضية:", self.f_status),
            ("تاريخ فتح الملف:", self.f_open_date),
            ("ملاحظات:", self.f_notes),
        ]
        for lbl_text, widget in fields:
            lbl = QLabel(lbl_text)
            lbl.setObjectName("form_label")
            form.addRow(lbl, widget)

        layout.addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        save_btn = make_btn("💾  حفظ القضية", "primary")
        save_btn.clicked.connect(self._save)
        cancel_btn = make_btn("إلغاء", "secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _load_clients(self, search=""):
        self.client_combo.clear()
        clients = db.get_clients(search)
        self._clients = clients
        for c in clients:
            self.client_combo.addItem(f"{c['code']} - {c['name']}", c["id"])

    def _filter_clients(self, text):
        self._load_clients(text)

    def _populate(self, d):
        # Select client
        for i in range(self.client_combo.count()):
            if self.client_combo.itemData(i) == d.get("client_id"):
                self.client_combo.setCurrentIndex(i)
                break

        def set_combo(cb, val):
            idx = cb.findText(val)
            if idx >= 0:
                cb.setCurrentIndex(idx)

        set_combo(self.f_client_role, d.get("client_role",""))
        set_combo(self.f_case_type, d.get("case_type",""))
        self.f_case_number.setText(d.get("case_number",""))
        self.f_case_year.setText(d.get("case_year",""))
        self.f_court.setText(d.get("court",""))
        self.f_circuit.setText(d.get("circuit",""))
        self.f_opponent.setText(d.get("opponent",""))
        self.f_opp_lawyer.setText(d.get("opponent_lawyer",""))
        self.f_subject.setText(d.get("subject",""))
        self.f_requests.setText(d.get("requests",""))
        self.f_last_action.setText(d.get("last_action",""))
        set_combo(self.f_status, d.get("status",""))
        if d.get("file_open_date"):
            try:
                parts = d["file_open_date"].split("-")
                self.f_open_date.setDate(QDate(int(parts[0]),int(parts[1]),int(parts[2])))
            except:
                pass
        self.f_notes.setText(d.get("notes",""))

    def _save(self):
        client_id = self.client_combo.currentData()
        if not client_id:
            show_error(self, "خطأ", "الرجاء اختيار العميل")
            return
        self.result_data = {
            "client_id": client_id,
            "client_role": self.f_client_role.currentText(),
            "case_type": self.f_case_type.currentText(),
            "case_number": self.f_case_number.text().strip(),
            "case_year": self.f_case_year.text().strip(),
            "court": self.f_court.text().strip(),
            "circuit": self.f_circuit.text().strip(),
            "opponent": self.f_opponent.text().strip(),
            "opponent_lawyer": self.f_opp_lawyer.text().strip(),
            "subject": self.f_subject.toPlainText().strip(),
            "requests": self.f_requests.toPlainText().strip(),
            "last_action": self.f_last_action.toPlainText().strip(),
            "status": self.f_status.currentText(),
            "file_open_date": self.f_open_date.date().toString("yyyy-MM-dd"),
            "notes": self.f_notes.toPlainText().strip(),
        }
        self.accept()

    def get_data(self):
        return getattr(self, "result_data", None)


class CasesPage(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Toolbar
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(10, 8, 10, 8)
        tl.setSpacing(10)

        title = QLabel("📁  إدارة القضايا")
        title.setObjectName("section_title")
        fnt = QFont(); fnt.setPointSize(14); fnt.setBold(True)
        title.setFont(fnt)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  بحث في القضايا...")
        self.search_input.setLayoutDirection(Qt.RightToLeft)
        self.search_input.setFixedWidth(220)
        self.search_input.textChanged.connect(self.refresh)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {COLORS['border']};
                border-radius: 20px;
                padding: 6px 15px;
                font-size: 13px;
                background: white;
            }}
            QLineEdit:focus {{ border: 2px solid {COLORS['gold']}; }}
        """)

        self.filter_status = QComboBox()
        self.filter_status.addItems(["كل الحالات"] + CASE_STATUSES)
        self.filter_status.setLayoutDirection(Qt.RightToLeft)
        self.filter_status.currentIndexChanged.connect(self.refresh)

        self.filter_type = QComboBox()
        self.filter_type.addItems(["كل الأنواع"] + CASE_TYPES)
        self.filter_type.setLayoutDirection(Qt.RightToLeft)
        self.filter_type.currentIndexChanged.connect(self.refresh)

        add_btn = make_btn("➕  إضافة قضية", "primary")
        add_btn.clicked.connect(self._add_case)

        tl.addWidget(title)
        tl.addStretch()
        tl.addWidget(QLabel("النوع:"))
        tl.addWidget(self.filter_type)
        tl.addWidget(QLabel("الحالة:"))
        tl.addWidget(self.filter_status)
        tl.addWidget(self.search_input)
        tl.addWidget(add_btn)
        layout.addWidget(toolbar)

        # Table
        self.table = make_table([
            "إجراءات", "الحالة", "آخر إجراء", "الدائرة", "المحكمة",
            "الخصم", "سنة القضية", "رقم القضية", "نوع القضية",
            "صفة العميل", "العميل", "كود القضية"
        ])
        self.table.doubleClicked.connect(self._open_archive)
        layout.addWidget(self.table)

        self.summary_lbl = QLabel("إجمالي القضايا: 0")
        self.summary_lbl.setStyleSheet(f"color: {COLORS['text_mid']}; font-size: 12px; padding: 5px;")
        self.summary_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(self.summary_lbl)

    def refresh(self):
        search = self.search_input.text().strip()
        status = self.filter_status.currentText()
        case_type = self.filter_type.currentText()
        if status == "كل الحالات":
            status = ""
        if case_type == "كل الأنواع":
            case_type = ""

        cases = db.get_cases(search=search, status=status, case_type=case_type)
        self.table.setRowCount(len(cases))
        self.table.setSortingEnabled(False)
        self._case_ids = []

        status_colors = {
            "متداولة": COLORS['success'],
            "منتهية": COLORS['danger'],
            "مؤجلة": COLORS['warning'],
            "مشطوبة": COLORS['gray_dark'],
            "محجوزة للحكم": COLORS['navy'],
        }

        for i, c in enumerate(cases):
            self._case_ids.append(c["id"])
            set_table_item(self.table, i, 0, c.get("code",""))
            set_table_item(self.table, i, 1, c.get("client_name",""))
            set_table_item(self.table, i, 2, c.get("client_role",""))
            set_table_item(self.table, i, 3, c.get("case_type",""))
            set_table_item(self.table, i, 4, c.get("case_number",""))
            set_table_item(self.table, i, 5, c.get("case_year",""))
            set_table_item(self.table, i, 6, c.get("opponent",""))
            set_table_item(self.table, i, 7, c.get("court",""))
            set_table_item(self.table, i, 8, c.get("circuit",""))
            set_table_item(self.table, i, 9, c.get("last_action",""))
            set_table_item(self.table, i, 10, c.get("status",""),
                           color=status_colors.get(c.get("status",""), COLORS['text_dark']))

            # Actions
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(3,2,3,2)
            btn_l.setSpacing(3)

            def make_action_btn(icon, tooltip, color, callback):
                b = QPushButton(icon)
                b.setFixedSize(28,28)
                b.setToolTip(tooltip)
                b.setCursor(Qt.PointingHandCursor)
                b.setStyleSheet(f"""
                    QPushButton {{
                        background: {color}; color: white;
                        border-radius: 4px; font-size: 13px;
                    }}
                    QPushButton:hover {{ opacity: 0.8; }}
                """)
                b.clicked.connect(callback)
                return b

            edit_b = QPushButton("✏")
            edit_b.setFixedSize(28,28)
            edit_b.setCursor(Qt.PointingHandCursor)
            edit_b.setStyleSheet(f"background: {COLORS['gold']}; color: {COLORS['navy']}; border-radius:4px; font-size:13px;")
            edit_b.clicked.connect(lambda _, cid=c["id"]: self._edit_case(cid))

            arch_b = QPushButton("📂")
            arch_b.setFixedSize(28,28)
            arch_b.setCursor(Qt.PointingHandCursor)
            arch_b.setStyleSheet(f"background: {COLORS['navy']}; color: white; border-radius:4px; font-size:13px;")
            arch_b.clicked.connect(lambda _, cid=c["id"], ap=c.get("archive_path",""): self._open_folder(ap))

            btn_l.addWidget(arch_b)
            if self.user["role"] == "admin":
                del_b = QPushButton("🗑")
                del_b.setFixedSize(28,28)
                del_b.setCursor(Qt.PointingHandCursor)
                del_b.setStyleSheet(f"background: {COLORS['danger']}; color: white; border-radius:4px; font-size:13px;")
                del_b.clicked.connect(lambda _, cid=c["id"]: self._delete_case(cid))
                btn_l.addWidget(del_b)

            btn_l.addWidget(edit_b)
            btn_l.addStretch()
            self.table.setCellWidget(i, 11, btn_w)

        self.table.setSortingEnabled(True)
        self.summary_lbl.setText(f"إجمالي القضايا: {len(cases)}")

    def _add_case(self):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية إضافة قضايا")
            return
        dlg = CaseDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.add_case(data)
                show_info(self, "تم", "تم إضافة القضية بنجاح وإنشاء مجلد الأرشيف")
                self.refresh()

    def _edit_case(self, case_id):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية التعديل")
            return
        case = db.get_case(case_id)
        if not case:
            return
        dlg = CaseDialog(self, case)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.update_case(case_id, data)
                show_info(self, "تم", "تم تحديث بيانات القضية")
                self.refresh()

    def _delete_case(self, case_id):
        if not confirm_delete(self, "هل تريد حذف هذه القضية وجميع بياناتها؟"):
            return
        db.delete_case(case_id)
        show_info(self, "تم", "تم حذف القضية")
        self.refresh()

    def _open_folder(self, path):
        if path and os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])
        else:
            show_error(self, "خطأ", "مجلد الأرشيف غير موجود")

    def _open_archive(self, index):
        row = index.row()
        if row < len(self._case_ids):
            case = db.get_case(self._case_ids[row])
            if case:
                self._open_folder(case.get("archive_path",""))
