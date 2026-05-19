"""
pages/sessions.py - Sessions Management Page
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialog, QFormLayout, QComboBox, QTextEdit,
    QFrame, QDateEdit, QTabWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import database as db
from widgets import (
    make_btn, make_input, make_combo, make_textarea,
    make_table, set_table_item, confirm_delete, show_info, show_error, make_date
)
from styles import COLORS


SESSION_STATUSES = ["قادمة", "تمت", "مؤجلة"]


class SessionDialog(QDialog):
    def __init__(self, parent=None, session_data=None, case_id=None):
        super().__init__(parent)
        self.session_data = session_data
        self.preset_case_id = case_id
        self.setWindowTitle("إضافة جلسة" if not session_data else "تعديل بيانات الجلسة")
        self.setMinimumWidth(580)
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()
        if session_data:
            self._populate(session_data)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("بيانات الجلسة")
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Case selection
        case_row = QHBoxLayout()
        case_lbl = QLabel("* القضية:")
        case_lbl.setObjectName("form_label")
        case_lbl.setFixedWidth(130)

        self.case_search = make_input("ابحث عن القضية...")
        self.case_search.textChanged.connect(self._filter_cases)

        self.case_combo = QComboBox()
        self.case_combo.setLayoutDirection(Qt.RightToLeft)
        self.case_combo.setMinimumWidth(280)
        self._load_cases()

        if self.preset_case_id:
            for i in range(self.case_combo.count()):
                if self.case_combo.itemData(i) == self.preset_case_id:
                    self.case_combo.setCurrentIndex(i)
                    break

        case_row.addWidget(self.case_combo)
        case_row.addWidget(self.case_search)
        case_row.addWidget(case_lbl)
        layout.addLayout(case_row)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        self.f_date = make_date()
        self.f_time = make_input("مثال: 10:30 ص")
        self.f_court = make_input("اسم المحكمة")
        self.f_circuit = make_input("الدائرة")
        self.f_prev_decision = make_textarea(rows=2)
        self.f_required = make_textarea(rows=2)
        self.f_result = make_textarea(rows=2)
        self.f_notes = make_textarea(rows=2)
        self.f_status = make_combo(SESSION_STATUSES)

        for lbl_text, widget in [
            ("* تاريخ الجلسة:", self.f_date),
            ("وقت الجلسة:", self.f_time),
            ("المحكمة:", self.f_court),
            ("الدائرة:", self.f_circuit),
            ("القرار السابق:", self.f_prev_decision),
            ("المطلوب في القادمة:", self.f_required),
            ("نتيجة الجلسة:", self.f_result),
            ("ملاحظات:", self.f_notes),
            ("حالة الجلسة:", self.f_status),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setObjectName("form_label")
            form.addRow(lbl, widget)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        save_btn = make_btn("💾  حفظ الجلسة", "primary")
        save_btn.clicked.connect(self._save)
        cancel_btn = make_btn("إلغاء", "secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _load_cases(self, search=""):
        self.case_combo.clear()
        cases = db.get_cases(search=search)
        self._cases = cases
        for c in cases:
            self.case_combo.addItem(f"{c['code']} - {c['case_number']} - {c['client_name']}", c["id"])

    def _filter_cases(self, text):
        self._load_cases(text)

    def _populate(self, d):
        for i in range(self.case_combo.count()):
            if self.case_combo.itemData(i) == d.get("case_id"):
                self.case_combo.setCurrentIndex(i)
                break
        if d.get("session_date"):
            try:
                p = d["session_date"].split("-")
                self.f_date.setDate(QDate(int(p[0]),int(p[1]),int(p[2])))
            except:
                pass
        self.f_time.setText(d.get("session_time",""))
        self.f_court.setText(d.get("court",""))
        self.f_circuit.setText(d.get("circuit",""))
        self.f_prev_decision.setText(d.get("previous_decision",""))
        self.f_required.setText(d.get("required_action",""))
        self.f_result.setText(d.get("result",""))
        self.f_notes.setText(d.get("notes",""))
        idx = self.f_status.findText(d.get("status","قادمة"))
        if idx >= 0:
            self.f_status.setCurrentIndex(idx)

    def _save(self):
        case_id = self.case_combo.currentData()
        if not case_id:
            show_error(self, "خطأ", "الرجاء اختيار القضية")
            return
        self.result_data = {
            "case_id": case_id,
            "session_date": self.f_date.date().toString("yyyy-MM-dd"),
            "session_time": self.f_time.text().strip(),
            "court": self.f_court.text().strip(),
            "circuit": self.f_circuit.text().strip(),
            "previous_decision": self.f_prev_decision.toPlainText().strip(),
            "required_action": self.f_required.toPlainText().strip(),
            "result": self.f_result.toPlainText().strip(),
            "notes": self.f_notes.toPlainText().strip(),
            "status": self.f_status.currentText(),
        }
        self.accept()

    def get_data(self):
        return getattr(self, "result_data", None)


class SessionsPage(QWidget):
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

        title = QLabel("📅  إدارة الجلسات")
        title.setObjectName("section_title")
        fnt = QFont(); fnt.setPointSize(14); fnt.setBold(True)
        title.setFont(fnt)

        self.filter_combo = QComboBox()
        self.filter_combo.setLayoutDirection(Qt.RightToLeft)
        self.filter_combo.addItems(["كل الجلسات", "جلسات اليوم", "جلسات الأسبوع", "الجلسات القادمة"])
        self.filter_combo.currentIndexChanged.connect(self.refresh)

        self.filter_status = QComboBox()
        self.filter_status.setLayoutDirection(Qt.RightToLeft)
        self.filter_status.addItems(["كل الحالات"] + SESSION_STATUSES)
        self.filter_status.currentIndexChanged.connect(self.refresh)

        add_btn = make_btn("➕  إضافة جلسة", "primary")
        add_btn.clicked.connect(self._add_session)

        tl.addWidget(title)
        tl.addStretch()
        tl.addWidget(QLabel("عرض:"))
        tl.addWidget(self.filter_combo)
        tl.addWidget(QLabel("الحالة:"))
        tl.addWidget(self.filter_status)
        tl.addWidget(add_btn)
        layout.addWidget(toolbar)

        # Table
        self.table = make_table([
            "إجراءات", "الحالة", "المطلوب", "نتيجة الجلسة",
            "الدائرة", "المحكمة", "الوقت", "التاريخ", "العميل", "القضية"
        ])
        self.table.setColumnWidth(0, 100)
        self.table.doubleClicked.connect(self._edit_selected)
        layout.addWidget(self.table)

        self.summary_lbl = QLabel("إجمالي الجلسات: 0")
        self.summary_lbl.setStyleSheet(f"color: {COLORS['text_mid']}; font-size: 12px; padding: 5px;")
        self.summary_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(self.summary_lbl)

    def refresh(self):
        view = self.filter_combo.currentText()
        status = self.filter_status.currentText()
        date_filter = None
        if view == "جلسات اليوم":
            date_filter = "today"
        elif view == "جلسات الأسبوع":
            date_filter = "week"
        elif view == "الجلسات القادمة":
            date_filter = "upcoming"

        if status == "كل الحالات":
            status = None

        sessions = db.get_sessions(date_filter=date_filter, status=status)
        self.table.setRowCount(len(sessions))
        self.table.setSortingEnabled(False)
        self._session_ids = [s["id"] for s in sessions]

        status_colors = {"قادمة": COLORS['warning'], "تمت": COLORS['success'], "مؤجلة": COLORS['danger']}

        for i, s in enumerate(sessions):
            set_table_item(self.table, i, 0, f"{s.get('case_code','')} - {s.get('case_number','')}")
            set_table_item(self.table, i, 1, s.get("client_name",""))
            set_table_item(self.table, i, 2, s.get("session_date",""))
            set_table_item(self.table, i, 3, s.get("session_time",""))
            set_table_item(self.table, i, 4, s.get("court",""))
            set_table_item(self.table, i, 5, s.get("circuit",""))
            set_table_item(self.table, i, 6, s.get("result",""))
            set_table_item(self.table, i, 7, s.get("required_action",""))
            set_table_item(self.table, i, 8, s.get("status",""),
                           color=status_colors.get(s.get("status",""), COLORS['text_dark']))

            # Actions
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(3,2,3,2)
            btn_l.setSpacing(3)

            edit_b = QPushButton("✏")
            edit_b.setFixedSize(28,28)
            edit_b.setCursor(Qt.PointingHandCursor)
            edit_b.setStyleSheet(f"background:{COLORS['gold']};color:{COLORS['navy']};border-radius:4px;font-size:13px;")
            edit_b.clicked.connect(lambda _, sid=s["id"]: self._edit_session(sid))

            btn_l.addWidget(edit_b)

            if self.user["role"] == "admin":
                del_b = QPushButton("🗑")
                del_b.setFixedSize(28,28)
                del_b.setCursor(Qt.PointingHandCursor)
                del_b.setStyleSheet(f"background:{COLORS['danger']};color:white;border-radius:4px;font-size:13px;")
                del_b.clicked.connect(lambda _, sid=s["id"]: self._delete_session(sid))
                btn_l.addWidget(del_b)

            btn_l.addStretch()
            self.table.setCellWidget(i, 9, btn_w)

        self.table.setSortingEnabled(True)
        self.summary_lbl.setText(f"إجمالي الجلسات: {len(sessions)}")

    def _add_session(self):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية إضافة جلسات")
            return
        dlg = SessionDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.add_session(data)
                show_info(self, "تم", "تم إضافة الجلسة بنجاح")
                self.refresh()

    def _edit_session(self, sid):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية التعديل")
            return
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM sessions WHERE id=?", (sid,))
        row = c.fetchone()
        conn.close()
        if not row:
            return
        dlg = SessionDialog(self, dict(row))
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.update_session(sid, data)
                show_info(self, "تم", "تم تحديث بيانات الجلسة")
                self.refresh()

    def _delete_session(self, sid):
        if not confirm_delete(self, "هل تريد حذف هذه الجلسة؟"):
            return
        db.delete_session(sid)
        show_info(self, "تم", "تم حذف الجلسة")
        self.refresh()

    def _edit_selected(self, index):
        row = index.row()
        if row < len(self._session_ids):
            self._edit_session(self._session_ids[row])
