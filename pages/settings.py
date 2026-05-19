"""
pages/settings.py - Settings, Users, and Backup
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTabWidget, QFormLayout, QSpinBox,
    QDialog, QComboBox, QFileDialog, QTableWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os, shutil, zipfile
from datetime import datetime
import database as db
from widgets import (
    make_btn, make_input, make_table, set_table_item,
    confirm_delete, show_info, show_error
)
from styles import COLORS


class SettingsPage(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        title = QLabel("⚙  الإعدادات والنسخ الاحتياطي")
        title.setObjectName("section_title")
        fnt = QFont(); fnt.setPointSize(14); fnt.setBold(True)
        title.setFont(fnt)
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.setLayoutDirection(Qt.RightToLeft)

        # Tab 1: Office settings
        office_tab = self._build_office_tab()
        tabs.addTab(office_tab, "🏛  بيانات المكتب")

        # Tab 2: Users
        if self.user["role"] == "admin":
            users_tab = self._build_users_tab()
            tabs.addTab(users_tab, "👥  المستخدمون")

        # Tab 3: Backup
        backup_tab = self._build_backup_tab()
        tabs.addTab(backup_tab, "💾  النسخ الاحتياطي")

        layout.addWidget(tabs)

    # ─── Office Settings Tab ──────────────────────────────────────────
    def _build_office_tab(self):
        widget = QWidget()
        widget.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(12)

        self.s_office_name   = make_input()
        self.s_office_sub    = make_input()
        self.s_lawyer_name   = make_input()
        self.s_phone         = make_input()
        self.s_address       = make_input()

        self.s_alert_days = QSpinBox()
        self.s_alert_days.setMinimum(1)
        self.s_alert_days.setMaximum(30)
        self.s_alert_days.setValue(int(db.get_setting("alert_days", "3")))
        self.s_alert_days.setLayoutDirection(Qt.RightToLeft)
        self.s_alert_days.setSuffix("  أيام")

        # Archive path
        arch_row = QHBoxLayout()
        self.s_archive_path = QLineEdit()
        self.s_archive_path.setLayoutDirection(Qt.RightToLeft)
        self.s_archive_path.setReadOnly(True)
        arch_browse = make_btn("تصفح", "secondary")
        arch_browse.setFixedWidth(80)
        arch_browse.clicked.connect(lambda: self._browse_folder(self.s_archive_path))
        arch_row.addWidget(self.s_archive_path)
        arch_row.addWidget(arch_browse)
        arch_w = QWidget(); arch_w.setLayout(arch_row)

        # Backup path
        back_row = QHBoxLayout()
        self.s_backup_path = QLineEdit()
        self.s_backup_path.setLayoutDirection(Qt.RightToLeft)
        self.s_backup_path.setReadOnly(True)
        back_browse = make_btn("تصفح", "secondary")
        back_browse.setFixedWidth(80)
        back_browse.clicked.connect(lambda: self._browse_folder(self.s_backup_path))
        back_row.addWidget(self.s_backup_path)
        back_row.addWidget(back_browse)
        back_w = QWidget(); back_w.setLayout(back_row)

        # Load current settings
        self.s_office_name.setText(db.get_setting("office_name"))
        self.s_office_sub.setText(db.get_setting("office_subtitle"))
        self.s_lawyer_name.setText(db.get_setting("lawyer_name"))
        self.s_phone.setText(db.get_setting("phone"))
        self.s_address.setText(db.get_setting("address"))
        self.s_archive_path.setText(db.get_setting("archive_path"))
        self.s_backup_path.setText(db.get_setting("backup_path"))

        for lbl_text, widget in [
            ("* اسم المكتب:", self.s_office_name),
            ("اسم فرعي:", self.s_office_sub),
            ("* اسم المحامي:", self.s_lawyer_name),
            ("رقم الهاتف:", self.s_phone),
            ("العنوان:", self.s_address),
            ("أيام التنبيه قبل الجلسة:", self.s_alert_days),
            ("مجلد الأرشيف:", arch_w),
            ("مجلد النسخ الاحتياطي:", back_w),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setObjectName("form_label")
            form.addRow(lbl, widget)

        layout.addLayout(form)

        save_btn = make_btn("💾  حفظ الإعدادات", "primary")
        save_btn.setFixedWidth(200)
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn, alignment=Qt.AlignLeft)
        layout.addStretch()

        return widget

    def _browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "اختر المجلد", line_edit.text())
        if folder:
            line_edit.setText(folder)

    def _save_settings(self):
        if self.user["role"] != "admin":
            show_error(self, "غير مسموح", "فقط المدير يمكنه تغيير الإعدادات")
            return
        db.set_setting("office_name", self.s_office_name.text().strip())
        db.set_setting("office_subtitle", self.s_office_sub.text().strip())
        db.set_setting("lawyer_name", self.s_lawyer_name.text().strip())
        db.set_setting("phone", self.s_phone.text().strip())
        db.set_setting("address", self.s_address.text().strip())
        db.set_setting("alert_days", str(self.s_alert_days.value()))
        db.set_setting("archive_path", self.s_archive_path.text().strip())
        db.set_setting("backup_path", self.s_backup_path.text().strip())
        show_info(self, "تم", "تم حفظ الإعدادات بنجاح\nستُطبق بعض الإعدادات عند إعادة تشغيل البرنامج")

    # ─── Users Tab ───────────────────────────────────────────────────
    def _build_users_tab(self):
        widget = QWidget()
        widget.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        toolbar = QHBoxLayout()
        title = QLabel("إدارة المستخدمين")
        title.setObjectName("section_title")

        add_btn = make_btn("➕  إضافة مستخدم", "primary")
        add_btn.clicked.connect(self._add_user)

        toolbar.addStretch()
        toolbar.addWidget(title)
        toolbar.addStretch()
        toolbar.addWidget(add_btn)
        layout.addLayout(toolbar)

        self.users_table = make_table([
            "إجراءات", "تاريخ الإنشاء", "الحالة", "الصلاحية", "الاسم الكامل", "اسم المستخدم"
        ])
        layout.addWidget(self.users_table)

        self._refresh_users()
        return widget

    def _refresh_users(self):
        users = db.get_users()
        self.users_table.setRowCount(len(users))
        self.users_table.setSortingEnabled(False)
        self._user_ids = [u["id"] for u in users]

        role_names = {"admin": "مدير", "employee": "موظف", "viewer": "مشاهدة فقط"}
        for i, u in enumerate(users):
            set_table_item(self.users_table, i, 0, u.get("username",""))
            set_table_item(self.users_table, i, 1, u.get("full_name",""))
            set_table_item(self.users_table, i, 2, role_names.get(u.get("role",""), u.get("role","")))
            status = "نشط" if u.get("is_active",1) else "معطل"
            set_table_item(self.users_table, i, 3, status,
                           color=COLORS['success'] if u.get("is_active",1) else COLORS['danger'])
            set_table_item(self.users_table, i, 4, u.get("created_at","")[:10])

            # Action buttons
            btn_w = QWidget()
            btn_l = QHBoxLayout(btn_w)
            btn_l.setContentsMargins(3,2,3,2)
            btn_l.setSpacing(3)

            edit_b = QPushButton("✏")
            edit_b.setFixedSize(28,28)
            edit_b.setCursor(Qt.PointingHandCursor)
            edit_b.setStyleSheet(f"background:{COLORS['gold']};color:{COLORS['navy']};border-radius:4px;")
            edit_b.clicked.connect(lambda _, uid=u["id"]: self._edit_user(uid))

            if u.get("username") != "admin":
                del_b = QPushButton("🗑")
                del_b.setFixedSize(28,28)
                del_b.setCursor(Qt.PointingHandCursor)
                del_b.setStyleSheet(f"background:{COLORS['danger']};color:white;border-radius:4px;")
                del_b.clicked.connect(lambda _, uid=u["id"]: self._delete_user(uid))
                btn_l.addWidget(del_b)

            btn_l.addWidget(edit_b)
            btn_l.addStretch()
            self.users_table.setCellWidget(i, 5, btn_w)

        self.users_table.setSortingEnabled(True)

    def _add_user(self):
        dlg = UserDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                try:
                    db.add_user(data)
                    show_info(self, "تم", "تم إضافة المستخدم بنجاح")
                    self._refresh_users()
                except Exception as e:
                    show_error(self, "خطأ", f"اسم المستخدم موجود بالفعل\n{e}")

    def _edit_user(self, uid):
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (uid,))
        row = c.fetchone()
        conn.close()
        if not row:
            return
        dlg = UserDialog(self, dict(row))
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if data:
                db.update_user(uid, data)
                show_info(self, "تم", "تم تحديث بيانات المستخدم")
                self._refresh_users()

    def _delete_user(self, uid):
        if not confirm_delete(self, "هل تريد حذف هذا المستخدم؟"):
            return
        db.delete_user(uid)
        show_info(self, "تم", "تم حذف المستخدم")
        self._refresh_users()

    # ─── Backup Tab ──────────────────────────────────────────────────
    def _build_backup_tab(self):
        widget = QWidget()
        widget.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Backup section
        backup_frame = QFrame()
        backup_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                border-top: 3px solid {COLORS['gold']};
            }}
        """)
        bf_layout = QVBoxLayout(backup_frame)
        bf_layout.setContentsMargins(20, 20, 20, 20)
        bf_layout.setSpacing(12)

        bk_title = QLabel("💾  إنشاء نسخة احتياطية")
        bk_title.setStyleSheet(f"color: {COLORS['navy']}; font-size: 15px; font-weight: bold;")
        bk_title.setAlignment(Qt.AlignRight)

        bk_desc = QLabel(
            "ينشئ هذا الخيار نسخة احتياطية كاملة من:\n"
            "• قاعدة البيانات (law_office.db)\n"
            "• مجلد الأرشيف الكامل\n\n"
            "يتم حفظ النسخة في مجلد Backups بتاريخ اليوم"
        )
        bk_desc.setAlignment(Qt.AlignRight)
        bk_desc.setStyleSheet(f"color: {COLORS['text_mid']}; font-size: 13px;")

        self.backup_status = QLabel("")
        self.backup_status.setAlignment(Qt.AlignRight)
        self.backup_status.setStyleSheet(f"color: {COLORS['success']}; font-size: 12px;")

        backup_btn = make_btn("📦  إنشاء نسخة احتياطية الآن", "primary")
        backup_btn.setFixedWidth(260)
        backup_btn.clicked.connect(self._create_backup)

        bf_layout.addWidget(bk_title)
        bf_layout.addWidget(bk_desc)
        bf_layout.addWidget(self.backup_status)
        bf_layout.addWidget(backup_btn, alignment=Qt.AlignLeft)
        layout.addWidget(backup_frame)

        # Restore section
        restore_frame = QFrame()
        restore_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                border-top: 3px solid {COLORS['warning']};
            }}
        """)
        rf_layout = QVBoxLayout(restore_frame)
        rf_layout.setContentsMargins(20, 20, 20, 20)
        rf_layout.setSpacing(12)

        rs_title = QLabel("🔄  استعادة نسخة احتياطية")
        rs_title.setStyleSheet(f"color: {COLORS['warning']}; font-size: 15px; font-weight: bold;")
        rs_title.setAlignment(Qt.AlignRight)

        rs_desc = QLabel(
            "⚠  تحذير: ستؤدي الاستعادة إلى استبدال قاعدة البيانات الحالية.\n"
            "تأكد من إنشاء نسخة احتياطية قبل الاستعادة."
        )
        rs_desc.setAlignment(Qt.AlignRight)
        rs_desc.setStyleSheet(f"color: {COLORS['danger']}; font-size: 13px;")

        restore_btn = make_btn("🔄  استعادة نسخة احتياطية", "secondary")
        restore_btn.setFixedWidth(260)
        restore_btn.clicked.connect(self._restore_backup)

        rf_layout.addWidget(rs_title)
        rf_layout.addWidget(rs_desc)
        rf_layout.addWidget(restore_btn, alignment=Qt.AlignLeft)
        layout.addWidget(restore_frame)
        layout.addStretch()

        return widget

    def _create_backup(self):
        backup_base = db.get_setting("backup_path",
            os.path.join(os.path.dirname(os.path.abspath(db.__file__)), "Backups"))
        os.makedirs(backup_base, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(backup_base, f"Backup_{timestamp}")
        os.makedirs(backup_folder, exist_ok=True)

        try:
            # Copy database
            db_path = db.DB_PATH
            if os.path.exists(db_path):
                shutil.copy2(db_path, os.path.join(backup_folder, "law_office.db"))

            # Copy archive folder
            archive_path = db.get_setting("archive_path",
                os.path.join(os.path.dirname(os.path.abspath(db.__file__)), "Archive"))
            if os.path.exists(archive_path):
                shutil.copytree(archive_path, os.path.join(backup_folder, "Archive"))

            # Create zip
            zip_path = backup_folder + ".zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(backup_folder):
                    for file in files:
                        fp = os.path.join(root, file)
                        zf.write(fp, os.path.relpath(fp, backup_folder))

            # Cleanup unzipped folder
            shutil.rmtree(backup_folder)

            self.backup_status.setText(f"✅  تم إنشاء النسخة الاحتياطية بنجاح:\n{zip_path}")
            show_info(self, "تم", f"تم إنشاء النسخة الاحتياطية بنجاح\n{zip_path}")

        except Exception as e:
            show_error(self, "خطأ في النسخ الاحتياطي", str(e))

    def _restore_backup(self):
        zip_path, _ = QFileDialog.getOpenFileName(
            self, "اختر ملف النسخة الاحتياطية", "",
            "ملفات ZIP (*.zip)"
        )
        if not zip_path:
            return

        from widgets import confirm_delete
        reply = confirm_delete(self,
            "⚠  تحذير!\n\nهذه العملية ستستبدل قاعدة البيانات الحالية.\nهل تريد الاستمرار؟")
        if not reply:
            return

        try:
            extract_tmp = os.path.join(os.path.dirname(zip_path), "_restore_tmp")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_tmp)

            restored_db = os.path.join(extract_tmp, "law_office.db")
            if os.path.exists(restored_db):
                shutil.copy2(restored_db, db.DB_PATH)

            restored_archive = os.path.join(extract_tmp, "Archive")
            archive_dest = db.get_setting("archive_path",
                os.path.join(os.path.dirname(os.path.abspath(db.__file__)), "Archive"))
            if os.path.exists(restored_archive):
                if os.path.exists(archive_dest):
                    shutil.rmtree(archive_dest)
                shutil.copytree(restored_archive, archive_dest)

            shutil.rmtree(extract_tmp)
            show_info(self, "تم", "تم استعادة النسخة الاحتياطية بنجاح!\nيُنصح بإعادة تشغيل البرنامج")

        except Exception as e:
            show_error(self, "خطأ في الاستعادة", str(e))


class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle("إضافة مستخدم" if not user_data else "تعديل بيانات المستخدم")
        self.setMinimumWidth(440)
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()
        if user_data:
            self._populate(user_data)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("بيانات المستخدم")
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        self.f_username  = make_input("اسم المستخدم للدخول")
        self.f_fullname  = make_input("الاسم الكامل")
        self.f_password  = QLineEdit()
        self.f_password.setEchoMode(QLineEdit.Password)
        self.f_password.setPlaceholderText("كلمة المرور (اتركها فارغة للإبقاء على الحالية)")
        self.f_password.setLayoutDirection(Qt.RightToLeft)
        self.f_role = QComboBox()
        self.f_role.setLayoutDirection(Qt.RightToLeft)
        self.f_role.addItems(["مدير|admin", "موظف|employee", "مشاهدة فقط|viewer"])
        self.f_active = QComboBox()
        self.f_active.setLayoutDirection(Qt.RightToLeft)
        self.f_active.addItems(["نشط", "معطل"])

        for lbl_text, widget in [
            ("* اسم المستخدم:", self.f_username),
            ("* الاسم الكامل:", self.f_fullname),
            ("كلمة المرور:", self.f_password),
            ("* الصلاحية:", self.f_role),
            ("الحالة:", self.f_active),
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
        self.f_username.setText(d.get("username",""))
        self.f_fullname.setText(d.get("full_name",""))
        role = d.get("role","viewer")
        for i in range(self.f_role.count()):
            if self.f_role.itemText(i).endswith(f"|{role}"):
                self.f_role.setCurrentIndex(i)
                break
        self.f_active.setCurrentIndex(0 if d.get("is_active",1) else 1)

    def _save(self):
        username = self.f_username.text().strip()
        fullname = self.f_fullname.text().strip()
        if not username or not fullname:
            show_error(self, "خطأ", "اسم المستخدم والاسم الكامل مطلوبان")
            return
        role_text = self.f_role.currentText()
        role_key = role_text.split("|")[-1]
        self.result_data = {
            "username": username,
            "full_name": fullname,
            "password": self.f_password.text().strip(),
            "role": role_key,
            "is_active": 1 if self.f_active.currentIndex() == 0 else 0,
        }
        self.accept()

    def get_data(self):
        return getattr(self, "result_data", None)
