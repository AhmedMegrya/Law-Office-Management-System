"""
pages/fees.py - Fees and Expenses Management
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialog, QFormLayout, QComboBox, QFrame,
    QDoubleSpinBox, QDateEdit, QTabWidget, QTextEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import database as db
from widgets import (
    make_btn, make_input, make_combo, make_textarea,
    make_table, set_table_item, confirm_delete, show_info, show_error, make_date
)
from styles import COLORS

PAYMENT_METHODS = ["نقدي", "تحويل بنكي", "شيك", "أخرى"]
EXPENSE_TYPES = ["رسوم قضائية", "مصاريف انتقال", "خبراء", "ترجمة", "إخطارات", "طباعة", "أخرى"]


def make_spinbox(parent=None):
    sb = QDoubleSpinBox(parent)
    sb.setMaximum(9999999.99)
    sb.setDecimals(2)
    sb.setSuffix("  ج.م")
    sb.setLayoutDirection(Qt.RightToLeft)
    return sb


class FeeDialog(QDialog):
    def __init__(self, parent=None, fee_data=None):
        super().__init__(parent)
        self.setWindowTitle("تسجيل أتعاب" if not fee_data else "تعديل الأتعاب")
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()
        if fee_data:
            self._populate(fee_data)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("بيانات الأتعاب")
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Case/Client selection
        cl_row = QHBoxLayout()
        cl_lbl = QLabel("العميل:")
        cl_lbl.setObjectName("form_label")
        self.client_combo = QComboBox()
        self.client_combo.setLayoutDirection(Qt.RightToLeft)
        clients = db.get_clients()
        self.client_combo.addItem("-- اختر العميل --", None)
        for c in clients:
            self.client_combo.addItem(f"{c['code']} - {c['name']}", c["id"])
        self.client_combo.currentIndexChanged.connect(self._load_cases)
        cl_row.addWidget(self.client_combo)
        cl_row.addWidget(cl_lbl)
        layout.addLayout(cl_row)

        cs_row = QHBoxLayout()
        cs_lbl = QLabel("القضية:")
        cs_lbl.setObjectName("form_label")
        self.case_combo = QComboBox()
        self.case_combo.setLayoutDirection(Qt.RightToLeft)
        cs_row.addWidget(self.case_combo)
        cs_row.addWidget(cs_lbl)
        layout.addLayout(cs_row)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        self.f_total = make_spinbox()
        self.f_paid = make_spinbox()
        self.f_method = make_combo(PAYMENT_METHODS)
        self.f_date = make_date()
        self.f_notes = make_textarea(rows=2)

        for lbl_text, widget in [
            ("إجمالي الأتعاب:", self.f_total),
            ("المدفوع:", self.f_paid),
            ("طريقة الدفع:", self.f_method),
            ("تاريخ الدفع:", self.f_date),
            ("ملاحظات:", self.f_notes),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setObjectName("form_label")
            form.addRow(lbl, widget)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        save_btn = make_btn("💾  حفظ", "primary")
        save_btn.clicked.connect(self._save)
        cancel_btn = make_btn("إلغاء", "secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _load_cases(self):
        client_id = self.client_combo.currentData()
        self.case_combo.clear()
        self.case_combo.addItem("-- اختر القضية --", None)
        if client_id:
            cases = db.get_cases(client_id=client_id)
            for c in cases:
                self.case_combo.addItem(f"{c['code']} - {c['case_number']}", c["id"])

    def _populate(self, d):
        for i in range(self.client_combo.count()):
            if self.client_combo.itemData(i) == d.get("client_id"):
                self.client_combo.setCurrentIndex(i)
                break
        self._load_cases()
        for i in range(self.case_combo.count()):
            if self.case_combo.itemData(i) == d.get("case_id"):
                self.case_combo.setCurrentIndex(i)
                break
        self.f_total.setValue(d.get("total_fees",0))
        self.f_paid.setValue(d.get("paid",0))
        idx = self.f_method.findText(d.get("payment_method",""))
        if idx >= 0:
            self.f_method.setCurrentIndex(idx)
        if d.get("payment_date"):
            try:
                p = d["payment_date"].split("-")
                self.f_date.setDate(QDate(int(p[0]),int(p[1]),int(p[2])))
            except:
                pass
        self.f_notes.setText(d.get("notes",""))

    def _save(self):
        self.result_data = {
            "client_id": self.client_combo.currentData(),
            "case_id": self.case_combo.currentData(),
            "total_fees": self.f_total.value(),
            "paid": self.f_paid.value(),
            "payment_method": self.f_method.currentText(),
            "payment_date": self.f_date.date().toString("yyyy-MM-dd"),
            "notes": self.f_notes.toPlainText().strip(),
        }
        self.accept()

    def get_data(self):
        return getattr(self, "result_data", None)


class FeesPage(QWidget):
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

        title = QLabel("💰  إدارة الأتعاب والمدفوعات")
        title.setObjectName("section_title")
        fnt = QFont(); fnt.setPointSize(14); fnt.setBold(True)
        title.setFont(fnt)

        add_btn = make_btn("➕  تسجيل أتعاب", "primary")
        add_btn.clicked.connect(self._add_fee)

        tl.addWidget(title)
        tl.addStretch()
        tl.addWidget(add_btn)
        layout.addWidget(toolbar)

        # Summary cards
        summary_row = QHBoxLayout()
        self.lbl_total = QLabel("إجمالي الأتعاب: 0 ج.م")
        self.lbl_paid = QLabel("المدفوع: 0 ج.م")
        self.lbl_remaining = QLabel("المتبقي: 0 ج.م")

        for lbl, color in [(self.lbl_total, COLORS['navy']),
                           (self.lbl_paid, COLORS['success']),
                           (self.lbl_remaining, COLORS['danger'])]:
            lbl.setStyleSheet(f"""
                background: white; color: {color};
                border: 1px solid {COLORS['border']}; border-radius: 8px;
                padding: 12px 20px; font-size: 14px; font-weight: bold;
                border-top: 3px solid {color};
            """)
            lbl.setAlignment(Qt.AlignCenter)
            summary_row.addWidget(lbl)

        layout.addLayout(summary_row)

        self.table = make_table([
            "إجراءات", "ملاحظات", "تاريخ الدفع", "طريقة الدفع",
            "المتبقي", "المدفوع", "إجمالي الأتعاب", "القضية", "العميل"
        ])
        layout.addWidget(self.table)

    def refresh(self):
        fees = db.get_fees()
        self.table.setRowCount(len(fees))
        self.table.setSortingEnabled(False)
        self._fee_ids = [f["id"] for f in fees]

        total = sum(f.get("total_fees",0) for f in fees)
        paid = sum(f.get("paid",0) for f in fees)
        remaining = sum(f.get("remaining",0) for f in fees)

        self.lbl_total.setText(f"إجمالي الأتعاب: {total:,.0f} ج.م")
        self.lbl_paid.setText(f"المدفوع: {paid:,.0f} ج.م")
        self.lbl_remaining.setText(f"المتبقي: {remaining:,.0f} ج.م")

        for i, f in enumerate(fees):
            set_table_item(self.table, i, 0, f.get("client_name",""))
            set_table_item(self.table, i, 1, f.get("case_code","") + " - " + f.get("case_number",""))
            set_table_item(self.table, i, 2, f"{f.get('total_fees',0):,.2f}")
            set_table_item(self.table, i, 3, f"{f.get('paid',0):,.2f}",
                           color=COLORS['success'])
            set_table_item(self.table, i, 4, f"{f.get('remaining',0):,.2f}",
                           color=COLORS['danger'] if f.get('remaining',0) > 0 else COLORS['success'])
            set_table_item(self.table, i, 5, f.get("payment_method",""))
            set_table_item(self.table, i, 6, f.get("payment_date",""))
            set_table_item(self.table, i, 7, f.get("notes",""))

            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(3,2,3,2)
            btn_l.setSpacing(3)

            edit_b = QPushButton("✏")
            edit_b.setFixedSize(28,28)
            edit_b.setCursor(Qt.PointingHandCursor)
            edit_b.setStyleSheet(f"background:{COLORS['gold']};color:{COLORS['navy']};border-radius:4px;font-size:13px;")
            edit_b.clicked.connect(lambda _, fid=f["id"]: self._edit_fee(fid))

            btn_l.addWidget(edit_b)
            btn_l.addStretch()
            self.table.setCellWidget(i, 8, btn_w)

        self.table.setSortingEnabled(True)

    def _add_fee(self):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية")
            return
        dlg = FeeDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.add_fee(data)
                show_info(self, "تم", "تم تسجيل الأتعاب بنجاح")
                self.refresh()

    def _edit_fee(self, fid):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية")
            return
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM fees WHERE id=?", (fid,))
        row = c.fetchone()
        conn.close()
        if not row:
            return
        dlg = FeeDialog(self, dict(row))
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                conn2 = db.get_connection()
                c2 = conn2.cursor()
                remaining = data["total_fees"] - data["paid"]
                c2.execute("""UPDATE fees SET client_id=?,case_id=?,total_fees=?,paid=?,remaining=?,
                             payment_method=?,payment_date=?,notes=? WHERE id=?""",
                           (data["client_id"], data["case_id"], data["total_fees"],
                            data["paid"], remaining, data["payment_method"],
                            data["payment_date"], data["notes"], fid))
                conn2.commit()
                conn2.close()
                show_info(self, "تم", "تم تحديث بيانات الأتعاب")
                self.refresh()


class ExpenseDialog(QDialog):
    def __init__(self, parent=None, expense_data=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة مصروف" if not expense_data else "تعديل مصروف")
        self.setMinimumWidth(480)
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()
        if expense_data:
            self._populate(expense_data)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("بيانات المصروف")
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        # Optional case
        self.case_combo = QComboBox()
        self.case_combo.setLayoutDirection(Qt.RightToLeft)
        self.case_combo.addItem("-- بدون قضية --", None)
        for c in db.get_cases():
            self.case_combo.addItem(f"{c['code']} - {c['case_number']} - {c['client_name']}", c["id"])

        self.f_type = make_combo(EXPENSE_TYPES)
        self.f_amount = make_spinbox()
        self.f_date = make_date()
        self.f_description = make_input("وصف المصروف")
        self.f_notes = make_textarea(rows=2)

        for lbl_text, widget in [
            ("القضية (اختياري):", self.case_combo),
            ("* نوع المصروف:", self.f_type),
            ("* المبلغ:", self.f_amount),
            ("* التاريخ:", self.f_date),
            ("البيان:", self.f_description),
            ("ملاحظات:", self.f_notes),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setObjectName("form_label")
            form.addRow(lbl, widget)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        save_btn = make_btn("💾  حفظ", "primary")
        save_btn.clicked.connect(self._save)
        cancel_btn = make_btn("إلغاء", "secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _populate(self, d):
        for i in range(self.case_combo.count()):
            if self.case_combo.itemData(i) == d.get("case_id"):
                self.case_combo.setCurrentIndex(i)
                break
        idx = self.f_type.findText(d.get("expense_type",""))
        if idx >= 0:
            self.f_type.setCurrentIndex(idx)
        self.f_amount.setValue(d.get("amount",0))
        if d.get("expense_date"):
            try:
                p = d["expense_date"].split("-")
                self.f_date.setDate(QDate(int(p[0]),int(p[1]),int(p[2])))
            except:
                pass
        self.f_description.setText(d.get("description",""))
        self.f_notes.setText(d.get("notes",""))

    def _save(self):
        self.result_data = {
            "case_id": self.case_combo.currentData(),
            "expense_type": self.f_type.currentText(),
            "amount": self.f_amount.value(),
            "expense_date": self.f_date.date().toString("yyyy-MM-dd"),
            "description": self.f_description.text().strip(),
            "notes": self.f_notes.toPlainText().strip(),
        }
        self.accept()

    def get_data(self):
        return getattr(self, "result_data", None)


class ExpensesPage(QWidget):
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

        title = QLabel("📊  إدارة المصروفات")
        title.setObjectName("section_title")
        fnt = QFont(); fnt.setPointSize(14); fnt.setBold(True)
        title.setFont(fnt)

        add_btn = make_btn("➕  إضافة مصروف", "primary")
        add_btn.clicked.connect(self._add_expense)

        tl.addWidget(title)
        tl.addStretch()
        tl.addWidget(add_btn)
        layout.addWidget(toolbar)

        self.total_lbl = QLabel("إجمالي المصروفات: 0 ج.م")
        self.total_lbl.setStyleSheet(f"""
            background: white; color: {COLORS['danger']};
            border: 1px solid {COLORS['border']}; border-radius: 8px;
            padding: 12px 20px; font-size: 14px; font-weight: bold;
            border-top: 3px solid {COLORS['danger']};
        """)
        self.total_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.total_lbl)

        self.table = make_table([
            "إجراءات", "ملاحظات", "البيان", "التاريخ",
            "المبلغ", "نوع المصروف", "القضية"
        ])
        layout.addWidget(self.table)

    def refresh(self):
        expenses = db.get_expenses()
        self.table.setRowCount(len(expenses))
        self.table.setSortingEnabled(False)
        self._expense_ids = [e["id"] for e in expenses]

        total = sum(e.get("amount",0) for e in expenses)
        self.total_lbl.setText(f"إجمالي المصروفات: {total:,.2f} ج.م")

        for i, e in enumerate(expenses):
            set_table_item(self.table, i, 0, e.get("case_code","") + " - " + e.get("case_number","") if e.get("case_code") else "عام")
            set_table_item(self.table, i, 1, e.get("expense_type",""))
            set_table_item(self.table, i, 2, f"{e.get('amount',0):,.2f}", color=COLORS['danger'])
            set_table_item(self.table, i, 3, e.get("expense_date",""))
            set_table_item(self.table, i, 4, e.get("description",""))
            set_table_item(self.table, i, 5, e.get("notes",""))

            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(3,2,3,2)
            btn_l.setSpacing(3)

            edit_b = QPushButton("✏")
            edit_b.setFixedSize(28,28)
            edit_b.setCursor(Qt.PointingHandCursor)
            edit_b.setStyleSheet(f"background:{COLORS['gold']};color:{COLORS['navy']};border-radius:4px;font-size:13px;")
            edit_b.clicked.connect(lambda _, eid=e["id"]: self._edit_expense(eid))

            if self.user["role"] == "admin":
                del_b = QPushButton("🗑")
                del_b.setFixedSize(28,28)
                del_b.setCursor(Qt.PointingHandCursor)
                del_b.setStyleSheet(f"background:{COLORS['danger']};color:white;border-radius:4px;font-size:13px;")
                del_b.clicked.connect(lambda _, eid=e["id"]: self._delete_expense(eid))
                btn_l.addWidget(del_b)

            btn_l.addWidget(edit_b)
            btn_l.addStretch()
            self.table.setCellWidget(i, 6, btn_w)

        self.table.setSortingEnabled(True)

    def _add_expense(self):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية")
            return
        dlg = ExpenseDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.add_expense(data)
                show_info(self, "تم", "تم إضافة المصروف بنجاح")
                self.refresh()

    def _edit_expense(self, eid):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية")
            return
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM expenses WHERE id=?", (eid,))
        row = c.fetchone()
        conn.close()
        if not row:
            return
        dlg = ExpenseDialog(self, dict(row))
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.update_expense(eid, data)
                show_info(self, "تم", "تم تحديث المصروف")
                self.refresh()

    def _delete_expense(self, eid):
        if not confirm_delete(self, "هل تريد حذف هذا المصروف؟"):
            return
        db.delete_expense(eid)
        show_info(self, "تم", "تم حذف المصروف")
        self.refresh()
