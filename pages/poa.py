"""
pages/powers_of_attorney.py - Powers of Attorney Management
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialog, QFormLayout, QComboBox, QFrame,
    QFileDialog, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import os, shutil, sys, subprocess
from datetime import datetime
import database as db
from widgets import (
    make_btn, make_input, make_combo, make_textarea,
    make_table, set_table_item, confirm_delete, show_info, show_error, make_date
)
from styles import COLORS

POA_TYPES = ["عام قضايا", "خاص", "بيع", "إدارة", "شركات", "أخرى"]


class POADialog(QDialog):
    def __init__(self, parent=None, poa_data=None):
        super().__init__(parent)
        self.poa_data = poa_data
        self.setWindowTitle("إضافة توكيل" if not poa_data else "تعديل بيانات التوكيل")
        self.setMinimumWidth(580)
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()
        if poa_data:
            self._populate(poa_data)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("بيانات التوكيل")
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        self.f_poa_number   = make_input("رقم التوكيل")
        self.f_poa_letter   = make_input("حرف التوكيل (إن وجد)")
        self.f_poa_year     = make_input("سنة التوكيل")
        self.f_notary       = make_input("مكتب التوثيق")

        # Client combo
        self.client_combo = QComboBox()
        self.client_combo.setLayoutDirection(Qt.RightToLeft)
        self.client_combo.addItem("-- اختر العميل (الموكل) --", None)
        for c in db.get_clients():
            self.client_combo.addItem(f"{c['code']} - {c['name']}", c["id"])

        self.f_attorney     = make_input("اسم الوكيل")
        self.f_poa_type     = make_combo(POA_TYPES)
        self.f_poa_date     = make_date()
        self.f_expiry_date  = make_date()
        self.f_notes        = make_textarea(rows=2)

        # File attachment
        file_row = QHBoxLayout()
        self.f_file_path = QLineEdit()
        self.f_file_path.setPlaceholderText("مسار ملف التوكيل (PDF أو صورة)...")
        self.f_file_path.setReadOnly(True)
        self.f_file_path.setLayoutDirection(Qt.RightToLeft)
        browse_btn = make_btn("📂  تصفح", "secondary")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse)
        file_row.addWidget(self.f_file_path)
        file_row.addWidget(browse_btn)
        file_widget = QWidget()
        file_widget.setLayout(file_row)

        for lbl_text, widget in [
            ("* رقم التوكيل:", self.f_poa_number),
            ("حرف التوكيل:", self.f_poa_letter),
            ("* سنة التوكيل:", self.f_poa_year),
            ("مكتب التوثيق:", self.f_notary),
            ("الموكل (العميل):", self.client_combo),
            ("اسم الوكيل:", self.f_attorney),
            ("* نوع التوكيل:", self.f_poa_type),
            ("* تاريخ التوكيل:", self.f_poa_date),
            ("تاريخ الانتهاء:", self.f_expiry_date),
            ("ملاحظات:", self.f_notes),
            ("ملف التوكيل:", file_widget),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setObjectName("form_label")
            form.addRow(lbl, widget)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        save_btn = make_btn("💾  حفظ التوكيل", "primary")
        save_btn.clicked.connect(self._save)
        cancel_btn = make_btn("إلغاء", "secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "اختر ملف التوكيل", "",
            "ملفات مدعومة (*.pdf *.jpg *.jpeg *.png *.tif *.tiff);;كل الملفات (*)"
        )
        if path:
            self.f_file_path.setText(path)

    def _populate(self, d):
        self.f_poa_number.setText(d.get("poa_number",""))
        self.f_poa_letter.setText(d.get("poa_letter",""))
        self.f_poa_year.setText(d.get("poa_year",""))
        self.f_notary.setText(d.get("notary_office",""))
        for i in range(self.client_combo.count()):
            if self.client_combo.itemData(i) == d.get("client_id"):
                self.client_combo.setCurrentIndex(i)
                break
        self.f_attorney.setText(d.get("attorney_name",""))
        idx = self.f_poa_type.findText(d.get("poa_type",""))
        if idx >= 0:
            self.f_poa_type.setCurrentIndex(idx)
        for field, key in [(self.f_poa_date, "poa_date"), (self.f_expiry_date, "expiry_date")]:
            if d.get(key):
                try:
                    p = d[key].split("-")
                    field.setDate(QDate(int(p[0]),int(p[1]),int(p[2])))
                except:
                    pass
        self.f_notes.setText(d.get("notes",""))
        self.f_file_path.setText(d.get("file_path",""))

    def _save(self):
        if not self.f_poa_number.text().strip():
            show_error(self, "خطأ", "رقم التوكيل مطلوب")
            return

        # Copy file to archive folder if new file selected
        file_path = self.f_file_path.text().strip()
        dest_path = file_path
        if file_path and os.path.exists(file_path) and not (self.poa_data and self.poa_data.get("file_path") == file_path):
            archive_base = db.get_setting("archive_path",
                os.path.join(os.path.dirname(os.path.abspath(db.__file__)), "Archive"))
            poa_folder = os.path.join(archive_base, "التوكيلات_العامة")
            os.makedirs(poa_folder, exist_ok=True)
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(poa_folder, file_name)
            base, ext = os.path.splitext(file_name)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(poa_folder, f"{base}_{counter}{ext}")
                counter += 1
            try:
                shutil.copy2(file_path, dest_path)
            except Exception as e:
                show_error(self, "خطأ في نسخ الملف", str(e))
                dest_path = file_path

        self.result_data = {
            "poa_number":   self.f_poa_number.text().strip(),
            "poa_letter":   self.f_poa_letter.text().strip(),
            "poa_year":     self.f_poa_year.text().strip(),
            "notary_office":self.f_notary.text().strip(),
            "client_id":    self.client_combo.currentData(),
            "attorney_name":self.f_attorney.text().strip(),
            "poa_type":     self.f_poa_type.currentText(),
            "poa_date":     self.f_poa_date.date().toString("yyyy-MM-dd"),
            "expiry_date":  self.f_expiry_date.date().toString("yyyy-MM-dd"),
            "notes":        self.f_notes.toPlainText().strip(),
            "file_path":    dest_path,
        }
        self.accept()

    def get_data(self):
        return getattr(self, "result_data", None)


class POAPage(QWidget):
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

        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(10, 8, 10, 8)
        tl.setSpacing(10)

        title = QLabel("📜  إدارة التوكيلات")
        title.setObjectName("section_title")
        fnt = QFont(); fnt.setPointSize(14); fnt.setBold(True)
        title.setFont(fnt)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  بحث برقم التوكيل أو اسم الموكل أو الوكيل...")
        self.search_input.setLayoutDirection(Qt.RightToLeft)
        self.search_input.setFixedWidth(300)
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

        add_btn = make_btn("➕  إضافة توكيل", "primary")
        add_btn.clicked.connect(self._add_poa)

        tl.addWidget(title)
        tl.addStretch()
        tl.addWidget(self.search_input)
        tl.addWidget(add_btn)
        layout.addWidget(toolbar)

        # Expiry alert
        self.alert_lbl = QLabel("")
        self.alert_lbl.setObjectName("alert_box")
        self.alert_lbl.setAlignment(Qt.AlignRight)
        self.alert_lbl.hide()
        layout.addWidget(self.alert_lbl)

        self.table = make_table([
            "إجراءات", "ملاحظات", "تاريخ الانتهاء",
            "تاريخ التوكيل", "نوع التوكيل", "الوكيل",
            "الموكل (العميل)", "مكتب التوثيق", "السنة",
            "حرف التوكيل", "رقم التوكيل"
        ])
        self.table.doubleClicked.connect(self._edit_selected)
        layout.addWidget(self.table)

        self.summary_lbl = QLabel("إجمالي التوكيلات: 0")
        self.summary_lbl.setStyleSheet(f"color: {COLORS['text_mid']}; font-size: 12px; padding: 5px;")
        self.summary_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(self.summary_lbl)

    def refresh(self):
        search = self.search_input.text().strip()
        poas = db.get_poas(search=search)
        self.table.setRowCount(len(poas))
        self.table.setSortingEnabled(False)
        self._poa_ids = [p["id"] for p in poas]

        today = datetime.now().strftime("%Y-%m-%d")
        expiring_soon = []

        for i, p in enumerate(poas):
            set_table_item(self.table, i, 0, p.get("poa_number",""))
            set_table_item(self.table, i, 1, p.get("poa_letter",""))
            set_table_item(self.table, i, 2, p.get("poa_year",""))
            set_table_item(self.table, i, 3, p.get("notary_office",""))
            set_table_item(self.table, i, 4, p.get("client_name",""))
            set_table_item(self.table, i, 5, p.get("attorney_name",""))
            set_table_item(self.table, i, 6, p.get("poa_type",""))
            set_table_item(self.table, i, 7, p.get("poa_date",""))

            expiry = p.get("expiry_date","")
            color = None
            if expiry and expiry != "2000-01-01":
                if expiry < today:
                    color = COLORS['danger']
                elif expiry <= today[:8] + "30":  # rough 30 days
                    color = COLORS['warning']
                    expiring_soon.append(f"{p.get('poa_number','')} (ينتهي {expiry})")
            set_table_item(self.table, i, 8, expiry if expiry and expiry != "2000-01-01" else "غير محدد", color=color)
            set_table_item(self.table, i, 9, p.get("notes",""))

            # Actions
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(3,2,3,2)
            btn_l.setSpacing(3)

            edit_b = QPushButton("✏")
            edit_b.setFixedSize(28,28)
            edit_b.setCursor(Qt.PointingHandCursor)
            edit_b.setStyleSheet(f"background:{COLORS['gold']};color:{COLORS['navy']};border-radius:4px;font-size:13px;")
            edit_b.clicked.connect(lambda _, pid=p["id"]: self._edit_poa(pid))

            file_path = p.get("file_path","")
            open_b = QPushButton("📂")
            open_b.setFixedSize(28,28)
            open_b.setCursor(Qt.PointingHandCursor)
            open_b.setToolTip("فتح ملف التوكيل")
            open_b.setStyleSheet(f"background:{COLORS['navy']};color:white;border-radius:4px;font-size:13px;")
            open_b.clicked.connect(lambda _, fp=file_path: self._open_file(fp))
            open_b.setEnabled(bool(file_path and os.path.exists(file_path)))

            btn_l.addWidget(open_b)

            if self.user["role"] == "admin":
                del_b = QPushButton("🗑")
                del_b.setFixedSize(28,28)
                del_b.setCursor(Qt.PointingHandCursor)
                del_b.setStyleSheet(f"background:{COLORS['danger']};color:white;border-radius:4px;font-size:13px;")
                del_b.clicked.connect(lambda _, pid=p["id"]: self._delete_poa(pid))
                btn_l.addWidget(del_b)

            btn_l.addWidget(edit_b)
            btn_l.addStretch()
            self.table.setCellWidget(i, 10, btn_w)

        self.table.setSortingEnabled(True)
        self.summary_lbl.setText(f"إجمالي التوكيلات: {len(poas)}")

        if expiring_soon:
            self.alert_lbl.setText("⚠  تنبيه: توكيلات قاربت على الانتهاء: " + " | ".join(expiring_soon))
            self.alert_lbl.show()
        else:
            self.alert_lbl.hide()

    def _add_poa(self):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية إضافة توكيلات")
            return
        dlg = POADialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.add_poa(data)
                show_info(self, "تم", "تم إضافة التوكيل بنجاح")
                self.refresh()

    def _edit_poa(self, pid):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية التعديل")
            return
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT p.*, cl.name as client_name FROM powers_of_attorney p LEFT JOIN clients cl ON p.client_id=cl.id WHERE p.id=?", (pid,))
        row = c.fetchone()
        conn.close()
        if not row:
            return
        dlg = POADialog(self, dict(row))
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.update_poa(pid, data)
                show_info(self, "تم", "تم تحديث بيانات التوكيل")
                self.refresh()

    def _delete_poa(self, pid):
        if not confirm_delete(self, "هل تريد حذف هذا التوكيل؟"):
            return
        db.delete_poa(pid)
        show_info(self, "تم", "تم حذف التوكيل")
        self.refresh()

    def _open_file(self, path):
        if path and os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])
        else:
            show_error(self, "خطأ", "الملف غير موجود")

    def _edit_selected(self, index):
        row = index.row()
        if row < len(self._poa_ids):
            self._edit_poa(self._poa_ids[row])
