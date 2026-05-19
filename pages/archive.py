"""
pages/archive.py - Electronic Archive Management Page
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialog, QFormLayout, QComboBox, QFrame,
    QFileDialog, QTableWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os, shutil, sys, subprocess
import database as db
from widgets import (
    make_btn, make_input, make_combo, make_textarea,
    make_table, set_table_item, confirm_delete, show_info, show_error
)
from styles import COLORS

DOC_TYPES = [
    "توكيلات", "عقود", "صحف دعاوى", "مذكرات",
    "حوافظ", "أحكام", "محاضر جلسات", "صور ومستندات", "أخرى"
]

SUBFOLDER_MAP = {
    "توكيلات":        "01_Powers",
    "عقود":           "02_Contracts",
    "صحف دعاوى":     "03_Lawsuits",
    "مذكرات":         "04_Memos",
    "حوافظ":          "05_Portfolios",
    "أحكام":          "06_Judgments",
    "محاضر جلسات":   "07_Reports",
    "صور ومستندات":  "08_Documents",
    "أخرى":           "09_Others",
}


class UploadDocDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("رفع مستند للأرشيف")
        self.setMinimumWidth(560)
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("رفع مستند جديد")
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        # Case selection
        self.case_combo = QComboBox()
        self.case_combo.setLayoutDirection(Qt.RightToLeft)
        self.case_combo.addItem("-- اختر القضية --", None)
        for c in db.get_cases():
            self.case_combo.addItem(f"{c['code']} - {c['case_number']} - {c['client_name']}", c["id"])

        # Client selection
        self.client_combo = QComboBox()
        self.client_combo.setLayoutDirection(Qt.RightToLeft)
        self.client_combo.addItem("-- اختر العميل --", None)
        for c in db.get_clients():
            self.client_combo.addItem(f"{c['code']} - {c['name']}", c["id"])

        self.f_doc_type = make_combo(DOC_TYPES)
        self.f_description = make_input("وصف المستند")

        # File selection
        file_row = QHBoxLayout()
        self.f_file_path = QLineEdit()
        self.f_file_path.setPlaceholderText("مسار الملف...")
        self.f_file_path.setReadOnly(True)
        self.f_file_path.setLayoutDirection(Qt.RightToLeft)
        browse_btn = make_btn("📂  تصفح", "secondary")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_file)
        file_row.addWidget(self.f_file_path)
        file_row.addWidget(browse_btn)

        file_widget = QWidget()
        file_widget.setLayout(file_row)

        for lbl_text, widget in [
            ("* القضية:", self.case_combo),
            ("العميل:", self.client_combo),
            ("* نوع المستند:", self.f_doc_type),
            ("الوصف:", self.f_description),
            ("* الملف:", file_widget),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setObjectName("form_label")
            form.addRow(lbl, widget)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        save_btn = make_btn("📤  رفع المستند", "primary")
        save_btn.clicked.connect(self._save)
        cancel_btn = make_btn("إلغاء", "secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "اختر الملف", "",
            "ملفات مدعومة (*.pdf *.docx *.doc *.jpg *.jpeg *.png *.tif *.tiff *.xlsx *.xls *.txt *.zip);;كل الملفات (*)"
        )
        if path:
            self.f_file_path.setText(path)

    def _save(self):
        case_id = self.case_combo.currentData()
        file_path = self.f_file_path.text().strip()

        if not case_id:
            show_error(self, "خطأ", "الرجاء اختيار القضية")
            return
        if not file_path or not os.path.exists(file_path):
            show_error(self, "خطأ", "الرجاء اختيار ملف صحيح")
            return

        # Get case archive path
        case = db.get_case(case_id)
        archive_path = case.get("archive_path", "") if case else ""
        doc_type = self.f_doc_type.currentText()
        subfolder = SUBFOLDER_MAP.get(doc_type, "09_أخرى")
        dest_folder = os.path.join(archive_path, subfolder)
        os.makedirs(dest_folder, exist_ok=True)

        # Copy file
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(dest_folder, file_name)
        # Handle duplicate names
        base, ext = os.path.splitext(file_name)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(dest_folder, f"{base}_{counter}{ext}")
            counter += 1

        try:
            shutil.copy2(file_path, dest_path)
        except Exception as e:
            show_error(self, "خطأ في النسخ", str(e))
            return

        self.result_data = {
            "case_id": case_id,
            "client_id": self.client_combo.currentData(),
            "doc_type": doc_type,
            "file_name": os.path.basename(dest_path),
            "file_path": dest_path,
            "description": self.f_description.text().strip(),
        }
        self.accept()

    def get_data(self):
        return getattr(self, "result_data", None)


class ArchivePage(QWidget):
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

        title = QLabel("🗂  الأرشيف الإلكتروني")
        title.setObjectName("section_title")
        fnt = QFont(); fnt.setPointSize(14); fnt.setBold(True)
        title.setFont(fnt)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  بحث بالعميل، القضية، الوصف...")
        self.search_input.setLayoutDirection(Qt.RightToLeft)
        self.search_input.setFixedWidth(250)
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

        self.filter_type = QComboBox()
        self.filter_type.setLayoutDirection(Qt.RightToLeft)
        self.filter_type.addItems(["كل الأنواع"] + DOC_TYPES)
        self.filter_type.currentIndexChanged.connect(self.refresh)

        upload_btn = make_btn("📤  رفع مستند", "primary")
        upload_btn.clicked.connect(self._upload_doc)

        tl.addWidget(title)
        tl.addStretch()
        tl.addWidget(QLabel("النوع:"))
        tl.addWidget(self.filter_type)
        tl.addWidget(self.search_input)
        tl.addWidget(upload_btn)
        layout.addWidget(toolbar)

        # Table
        self.table = make_table([
            "إجراءات", "تاريخ الإضافة", "الوصف",
            "نوع المستند", "اسم الملف", "القضية", "العميل"
        ])
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(4, 200)
        self.table.doubleClicked.connect(self._open_selected)
        layout.addWidget(self.table)

        self.summary_lbl = QLabel("إجمالي المستندات: 0")
        self.summary_lbl.setStyleSheet(f"color: {COLORS['text_mid']}; font-size: 12px; padding: 5px;")
        self.summary_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(self.summary_lbl)

    def refresh(self):
        search = self.search_input.text().strip()
        doc_type = self.filter_type.currentText()
        if doc_type == "كل الأنواع":
            doc_type = None

        docs = db.get_documents(doc_type=doc_type, search=search)
        self.table.setRowCount(len(docs))
        self.table.setSortingEnabled(False)
        self._doc_ids = [d["id"] for d in docs]
        self._doc_paths = [d.get("file_path","") for d in docs]

        for i, d in enumerate(docs):
            set_table_item(self.table, i, 0, d.get("client_name",""))
            set_table_item(self.table, i, 1, d.get("case_code","") + " - " + d.get("case_number",""))
            set_table_item(self.table, i, 2, d.get("file_name",""))
            set_table_item(self.table, i, 3, d.get("doc_type",""), color=COLORS['navy'])
            set_table_item(self.table, i, 4, d.get("description",""))
            set_table_item(self.table, i, 5, d.get("added_date",""))

            # Actions
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(3,2,3,2)
            btn_l.setSpacing(3)

            open_b = QPushButton("📂")
            open_b.setFixedSize(28,28)
            open_b.setToolTip("فتح الملف")
            open_b.setCursor(Qt.PointingHandCursor)
            open_b.setStyleSheet(f"background:{COLORS['navy']};color:white;border-radius:4px;font-size:13px;")
            open_b.clicked.connect(lambda _, p=d.get("file_path",""): self._open_file(p))

            btn_l.addWidget(open_b)

            if self.user["role"] == "admin":
                del_b = QPushButton("🗑")
                del_b.setFixedSize(28,28)
                del_b.setToolTip("حذف")
                del_b.setCursor(Qt.PointingHandCursor)
                del_b.setStyleSheet(f"background:{COLORS['danger']};color:white;border-radius:4px;font-size:13px;")
                del_b.clicked.connect(lambda _, did=d["id"]: self._delete_doc(did))
                btn_l.addWidget(del_b)

            btn_l.addStretch()
            self.table.setCellWidget(i, 6, btn_w)

        self.table.setSortingEnabled(True)
        self.summary_lbl.setText(f"إجمالي المستندات: {len(docs)}")

    def _upload_doc(self):
        if self.user["role"] == "viewer":
            show_error(self, "غير مسموح", "ليس لديك صلاحية رفع مستندات")
            return
        dlg = UploadDocDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.add_document(data)
                show_info(self, "تم", f"تم رفع المستند بنجاح\nتم حفظه في: {data['file_path']}")
                self.refresh()

    def _open_file(self, path):
        if path and os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])
        else:
            show_error(self, "خطأ", "الملف غير موجود على القرص\nقد يكون قد تم نقله أو حذفه")

    def _open_selected(self, index):
        row = index.row()
        if row < len(self._doc_paths):
            self._open_file(self._doc_paths[row])

    def _delete_doc(self, did):
        if not confirm_delete(self, "هل تريد حذف هذا المستند من الأرشيف؟\nسيتم حذف الملف من القرص أيضًا."):
            return
        file_path = db.delete_document(did)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        show_info(self, "تم", "تم حذف المستند من الأرشيف")
        self.refresh()
