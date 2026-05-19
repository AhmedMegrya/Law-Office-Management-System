"""
pages/clients.py - Clients Management Page
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialog, QFormLayout, QComboBox, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QAbstractItemView, QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
import database as db
from widgets import (
    make_btn, make_label, make_input, make_combo, make_textarea,
    make_table, set_table_item, confirm_delete, show_info, show_error,
    SectionHeader, FormRow
)
from styles import COLORS


class ClientDialog(QDialog):
    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.client_data = client_data
        self.setWindowTitle("إضافة عميل" if not client_data else "تعديل بيانات العميل")
        self.setMinimumWidth(550)
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()
        if client_data:
            self._populate(client_data)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("بيانات العميل")
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Form fields
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(12)

        self.f_name = make_input("الاسم الكامل للعميل")
        self.f_phone = make_input("رقم الهاتف")
        self.f_whatsapp = make_input("رقم الواتساب")
        self.f_national_id = make_input("الرقم القومي")
        self.f_address = make_input("العنوان الكامل")
        self.f_email = make_input("البريد الإلكتروني")
        self.f_type = make_combo(["فرد", "شركة"])
        self.f_notes = make_textarea(rows=3)

        for label, widget in [
            ("* الاسم:", self.f_name),
            ("الهاتف:", self.f_phone),
            ("واتساب:", self.f_whatsapp),
            ("الرقم القومي:", self.f_national_id),
            ("العنوان:", self.f_address),
            ("البريد الإلكتروني:", self.f_email),
            ("نوع العميل:", self.f_type),
            ("ملاحظات:", self.f_notes),
        ]:
            lbl = QLabel(label)
            lbl.setObjectName("form_label")
            form.addRow(lbl, widget)

        layout.addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        save_btn = make_btn("💾  حفظ", "primary")
        save_btn.clicked.connect(self._save)
        cancel_btn = make_btn("إلغاء", "secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _populate(self, d):
        self.f_name.setText(d.get("name",""))
        self.f_phone.setText(d.get("phone",""))
        self.f_whatsapp.setText(d.get("whatsapp",""))
        self.f_national_id.setText(d.get("national_id",""))
        self.f_address.setText(d.get("address",""))
        self.f_email.setText(d.get("email",""))
        idx = self.f_type.findText(d.get("client_type","فرد"))
        if idx >= 0:
            self.f_type.setCurrentIndex(idx)
        self.f_notes.setText(d.get("notes",""))

    def _save(self):
        name = self.f_name.text().strip()
        if not name:
            show_error(self, "خطأ", "اسم العميل مطلوب")
            return
        self.result_data = {
            "name": name,
            "phone": self.f_phone.text().strip(),
            "whatsapp": self.f_whatsapp.text().strip(),
            "national_id": self.f_national_id.text().strip(),
            "address": self.f_address.text().strip(),
            "email": self.f_email.text().strip(),
            "client_type": self.f_type.currentText(),
            "notes": self.f_notes.toPlainText().strip(),
        }
        self.accept()

    def get_data(self):
        return getattr(self, "result_data", None)


class ClientsPage(QWidget):
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
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 8, 10, 8)
        toolbar_layout.setSpacing(10)

        title = QLabel("👤  إدارة العملاء")
        title.setObjectName("section_title")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  بحث بالاسم، الهاتف، الكود...")
        self.search_input.setLayoutDirection(Qt.RightToLeft)
        self.search_input.setFixedWidth(280)
        self.search_input.textChanged.connect(self.refresh)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {COLORS['border']};
                border-radius: 20px;
                padding: 6px 15px;
                font-size: 13px;
                background: white;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['gold']};
            }}
        """)

        add_btn = make_btn("➕  إضافة عميل", "primary")
        add_btn.clicked.connect(self._add_client)

        toolbar_layout.addWidget(title)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(add_btn)

        layout.addWidget(toolbar)

        # Table
        self.table = make_table([
            "إجراءات", "الملاحظات", "نوع العميل", "البريد الإلكتروني",
            "العنوان", "الرقم القومي", "الهاتف", "اسم العميل", "الكود"
        ])
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(7, 180)
        self.table.doubleClicked.connect(self._view_client)
        layout.addWidget(self.table)

        # Summary bar
        self.summary_lbl = QLabel("إجمالي العملاء: 0")
        self.summary_lbl.setStyleSheet(f"color: {COLORS['text_mid']}; font-size: 12px; padding: 5px;")
        self.summary_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(self.summary_lbl)

    def refresh(self):
        search = self.search_input.text().strip()
        clients = db.get_clients(search)
        self.table.setRowCount(len(clients))
        self.table.setSortingEnabled(False)

        for i, c in enumerate(clients):
            set_table_item(self.table, i, 0, c.get("code",""))
            set_table_item(self.table, i, 1, c.get("name",""))
            set_table_item(self.table, i, 2, c.get("phone",""))
            set_table_item(self.table, i, 3, c.get("national_id",""))
            set_table_item(self.table, i, 4, c.get("address",""))
            set_table_item(self.table, i, 5, c.get("email",""))
            set_table_item(self.table, i, 6, c.get("client_type",""))
            set_table_item(self.table, i, 7, c.get("notes",""))

            # Action buttons cell
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(3, 2, 3, 2)
            btn_layout.setSpacing(4)

            edit_btn = QPushButton("✏")
            edit_btn.setFixedSize(28, 28)
            edit_btn.setToolTip("تعديل")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['gold']}; color: {COLORS['navy']};
                    border-radius: 4px; font-size: 14px; font-weight: bold;
                }}
                QPushButton:hover {{ background: {COLORS['gold_light']}; }}
            """)
            edit_btn.clicked.connect(lambda _, cid=c["id"]: self._edit_client(cid))

            if self.user["role"] in ("admin",):
                del_btn = QPushButton("🗑")
                del_btn.setFixedSize(28, 28)
                del_btn.setToolTip("حذف")
                del_btn.setCursor(Qt.PointingHandCursor)
                del_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {COLORS['danger']}; color: white;
                        border-radius: 4px; font-size: 14px;
                    }}
                    QPushButton:hover {{ background: #A02020; }}
                """)
                del_btn.clicked.connect(lambda _, cid=c["id"]: self._delete_client(cid))
                btn_layout.addWidget(del_btn)

            btn_layout.addWidget(edit_btn)
            btn_layout.addStretch()
            self.table.setCellWidget(i, 8, btn_widget)

        self.table.setSortingEnabled(True)
        self.summary_lbl.setText(f"إجمالي العملاء: {len(clients)}")

    def _add_client(self):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية إضافة عملاء")
            return
        dlg = ClientDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.add_client(data)
                show_info(self, "تم", "تم إضافة العميل بنجاح")
                self.refresh()

    def _edit_client(self, cid):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية التعديل")
            return
        client = db.get_client(cid)
        if not client:
            return
        dlg = ClientDialog(self, client)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.update_client(cid, data)
                show_info(self, "تم", "تم تحديث بيانات العميل")
                self.refresh()

    def _delete_client(self, cid):
        if not confirm_delete(self, "هل تريد حذف هذا العميل وجميع بياناته؟"):
            return
        db.delete_client(cid)
        show_info(self, "تم", "تم حذف العميل")
        self.refresh()

    def _view_client(self, index):
        row = index.row()
        # Get the code from column 0
        code_item = self.table.item(row, 0)
        if code_item:
            pass  # Could open detail view
