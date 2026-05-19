"""
pages/reports.py - Reports Generation Page
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QDateEdit, QGroupBox, QScrollArea,
    QGridLayout, QDialog, QTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
import database as db
from widgets import make_btn, make_combo, make_date, show_info, show_error
from styles import COLORS
from datetime import datetime


def build_html_report(title, office_name, office_sub, content_rows, headers, summary=""):
    """Build a styled Arabic RTL HTML report."""
    rows_html = ""
    for row in content_rows:
        cells = "".join(f"<td>{cell}</td>" for cell in row)
        rows_html += f"<tr>{cells}</tr>"

    headers_html = "".join(f"<th>{h}</th>" for h in headers)

    return f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Arial', sans-serif; direction: rtl; margin: 30px; color: #1A1208; }}
        .header {{ background: #0D1B3E; color: white; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ color: #C9A84C; margin: 0; font-size: 20px; }}
        .header p {{ margin: 5px 0 0 0; font-size: 13px; color: #B0A898; }}
        .report-title {{ color: #0D1B3E; font-size: 16px; font-weight: bold;
                         border-bottom: 2px solid #C9A84C; padding-bottom: 8px; margin-bottom: 15px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th {{ background: #0D1B3E; color: #C9A84C; padding: 10px; text-align: right; font-size: 13px; }}
        td {{ padding: 8px 10px; border: 1px solid #E8E6E0; font-size: 12px; text-align: right; }}
        tr:nth-child(even) {{ background: #F5F3EE; }}
        .summary {{ background: #FFF8E1; border: 1px solid #B8860B;
                    border-radius: 6px; padding: 12px; margin-top: 15px; font-weight: bold; }}
        .footer {{ text-align: center; color: #6B6155; font-size: 11px;
                   margin-top: 30px; border-top: 1px solid #D4C5A0; padding-top: 10px; }}
        .date-info {{ color: #6B6155; font-size: 12px; margin-bottom: 15px; }}
    </style>
    </head>
    <body>
    <div class="header">
        <h1>⚖ {office_name}</h1>
        <p>{office_sub}</p>
    </div>
    <div class="report-title">📋 {title}</div>
    <p class="date-info">تاريخ الطباعة: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    <table>
        <thead><tr>{headers_html}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    {"<div class='summary'>" + summary + "</div>" if summary else ""}
    <div class="footer">
        {office_name} - {office_sub} | نظام إدارة مكتب المحاماة
    </div>
    </body></html>
    """


class PrintPreviewDialog(QDialog):
    """Simple print preview dialog."""
    def __init__(self, html_content, title="تقرير", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"معاينة الطباعة - {title}")
        self.setMinimumSize(800, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        self.html_content = html_content

        layout = QVBoxLayout(self)

        btn_row = QHBoxLayout()
        print_btn = make_btn("🖨  طباعة", "primary")
        print_btn.clicked.connect(self._print)
        close_btn = make_btn("إغلاق", "secondary")
        close_btn.clicked.connect(self.reject)
        btn_row.addWidget(close_btn)
        btn_row.addStretch()
        btn_row.addWidget(print_btn)
        layout.addLayout(btn_row)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setHtml(html_content)
        layout.addWidget(self.preview)

    def _print(self):
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)
        if dlg.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setHtml(self.html_content)
            doc.print_(printer)
            show_info(self, "تم", "تمت إرسال التقرير للطباعة")


class ReportCard(QFrame):
    """Clickable report card."""
    def __init__(self, icon, title, description, callback, parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(130)
        self.callback = callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignRight)

        icon_title = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 28px; color: {COLORS['gold']};")
        icon_title.addStretch()
        icon_title.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['navy']};")
        title_lbl.setAlignment(Qt.AlignRight)

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(f"font-size: 11px; color: {COLORS['gray_dark']};")
        desc_lbl.setAlignment(Qt.AlignRight)
        desc_lbl.setWordWrap(True)

        btn = make_btn("📄  إنشاء التقرير", "primary")
        btn.clicked.connect(callback)

        layout.addLayout(icon_title)
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)
        layout.addWidget(btn)


class ReportsPage(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()

    def _get_office(self):
        return (
            db.get_setting("office_name", "مكتب المستشار/ أحمد شعبان مجرية"),
            db.get_setting("office_subtitle", "للمحاماة والاستشارات القانونية")
        )

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        title = QLabel("📋  التقارير")
        title.setObjectName("section_title")
        fnt = QFont(); fnt.setPointSize(14); fnt.setBold(True)
        title.setFont(fnt)
        layout.addWidget(title)

        # Scroll area for report cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content.setLayoutDirection(Qt.RightToLeft)
        grid = QGridLayout(content)
        grid.setSpacing(15)
        grid.setContentsMargins(5, 5, 5, 5)

        reports = [
            ("👤", "تقرير العملاء", "قائمة بجميع العملاء وبياناتهم", self._report_clients),
            ("📁", "تقرير القضايا المتداولة", "جميع القضايا النشطة حاليًا", self._report_active_cases),
            ("📅", "جلسات اليوم", "جدول جلسات يوم اليوم", self._report_today_sessions),
            ("📅", "جلسات الأسبوع", "جدول جلسات الأسبوع القادم", self._report_week_sessions),
            ("💰", "تقرير الأتعاب والمدفوعات", "كشف الأتعاب والمدفوعات والمتبقيات", self._report_fees),
            ("📊", "تقرير المصروفات", "كشف بجميع المصروفات", self._report_expenses),
            ("📜", "تقرير التوكيلات", "قائمة بجميع التوكيلات", self._report_poas),
            ("🗂", "تقرير الأرشيف", "قائمة بجميع المستندات المؤرشفة", self._report_archive),
            ("⚖", "كشف حساب عميل", "تقرير مالي تفصيلي لعميل محدد", self._report_client_statement),
        ]

        row, col = 0, 0
        for icon, title_text, desc, cb in reports:
            card = ReportCard(icon, title_text, desc, cb)
            grid.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _show_report(self, html, title):
        dlg = PrintPreviewDialog(html, title, self)
        dlg.exec_()

    def _report_clients(self):
        office, sub = self._get_office()
        clients = db.get_clients()
        rows = [[c.get("code",""), c.get("name",""), c.get("phone",""),
                 c.get("client_type",""), c.get("address",""), c.get("created_at","")[:10]]
                for c in clients]
        headers = ["تاريخ الإضافة", "العنوان", "النوع", "الهاتف", "الاسم", "الكود"]
        html = build_html_report(
            "تقرير العملاء", office, sub, rows, headers,
            f"إجمالي العملاء: {len(clients)} عميل"
        )
        self._show_report(html, "تقرير العملاء")

    def _report_active_cases(self):
        office, sub = self._get_office()
        cases = db.get_cases(status="متداولة")
        rows = [[c.get("code",""), c.get("client_name",""), c.get("case_number",""),
                 c.get("case_type",""), c.get("court",""), c.get("last_action","")]
                for c in cases]
        headers = ["آخر إجراء", "المحكمة", "نوع القضية", "رقم القضية", "العميل", "كود القضية"]
        html = build_html_report(
            "تقرير القضايا المتداولة", office, sub, rows, headers,
            f"إجمالي القضايا المتداولة: {len(cases)} قضية"
        )
        self._show_report(html, "القضايا المتداولة")

    def _report_today_sessions(self):
        office, sub = self._get_office()
        sessions = db.get_sessions(date_filter="today")
        rows = [[s.get("case_code",""), s.get("client_name",""), s.get("session_time",""),
                 s.get("court",""), s.get("circuit",""), s.get("required_action",""), s.get("status","")]
                for s in sessions]
        headers = ["الحالة", "المطلوب", "الدائرة", "المحكمة", "الوقت", "العميل", "القضية"]
        html = build_html_report(
            f"جلسات اليوم - {datetime.now().strftime('%Y-%m-%d')}",
            office, sub, rows, headers,
            f"إجمالي الجلسات: {len(sessions)}"
        )
        self._show_report(html, "جلسات اليوم")

    def _report_week_sessions(self):
        office, sub = self._get_office()
        sessions = db.get_sessions(date_filter="week")
        rows = [[s.get("session_date",""), s.get("case_code",""), s.get("client_name",""),
                 s.get("session_time",""), s.get("court",""), s.get("status","")]
                for s in sessions]
        headers = ["الحالة", "المحكمة", "الوقت", "العميل", "القضية", "التاريخ"]
        html = build_html_report(
            "جلسات الأسبوع القادم", office, sub, rows, headers,
            f"إجمالي الجلسات: {len(sessions)}"
        )
        self._show_report(html, "جلسات الأسبوع")

    def _report_fees(self):
        office, sub = self._get_office()
        fees = db.get_fees()
        rows = [[f.get("client_name",""), f.get("case_code",""), f"{f.get('total_fees',0):,.2f}",
                 f"{f.get('paid',0):,.2f}", f"{f.get('remaining',0):,.2f}", f.get("payment_method","")]
                for f in fees]
        headers = ["طريقة الدفع", "المتبقي (ج.م)", "المدفوع (ج.م)", "الإجمالي (ج.م)", "القضية", "العميل"]
        total = sum(f.get("total_fees",0) for f in fees)
        paid = sum(f.get("paid",0) for f in fees)
        remaining = sum(f.get("remaining",0) for f in fees)
        html = build_html_report(
            "تقرير الأتعاب والمدفوعات", office, sub, rows, headers,
            f"الإجمالي: {total:,.2f} ج.م  |  المدفوع: {paid:,.2f} ج.م  |  المتبقي: {remaining:,.2f} ج.م"
        )
        self._show_report(html, "الأتعاب والمدفوعات")

    def _report_expenses(self):
        office, sub = self._get_office()
        expenses = db.get_expenses()
        rows = [[e.get("expense_date",""), e.get("expense_type",""),
                 f"{e.get('amount',0):,.2f}", e.get("description",""),
                 e.get("case_code","") or "عام"]
                for e in expenses]
        headers = ["القضية", "البيان", "المبلغ (ج.م)", "نوع المصروف", "التاريخ"]
        total = sum(e.get("amount",0) for e in expenses)
        html = build_html_report(
            "تقرير المصروفات", office, sub, rows, headers,
            f"إجمالي المصروفات: {total:,.2f} ج.م"
        )
        self._show_report(html, "المصروفات")

    def _report_poas(self):
        office, sub = self._get_office()
        poas = db.get_poas()
        rows = [[p.get("poa_number",""), p.get("poa_year",""), p.get("client_name",""),
                 p.get("attorney_name",""), p.get("poa_type",""), p.get("poa_date",""),
                 p.get("expiry_date","") or "غير محدد"]
                for p in poas]
        headers = ["تاريخ الانتهاء", "تاريخ التوكيل", "نوع التوكيل", "الوكيل", "الموكل", "السنة", "رقم التوكيل"]
        html = build_html_report(
            "تقرير التوكيلات", office, sub, rows, headers,
            f"إجمالي التوكيلات: {len(poas)}"
        )
        self._show_report(html, "التوكيلات")

    def _report_archive(self):
        office, sub = self._get_office()
        docs = db.get_documents()
        rows = [[d.get("client_name",""), d.get("case_code",""), d.get("doc_type",""),
                 d.get("file_name",""), d.get("description",""), d.get("added_date","")]
                for d in docs]
        headers = ["تاريخ الإضافة", "الوصف", "اسم الملف", "نوع المستند", "القضية", "العميل"]
        html = build_html_report(
            "تقرير الأرشيف الإلكتروني", office, sub, rows, headers,
            f"إجمالي المستندات: {len(docs)}"
        )
        self._show_report(html, "الأرشيف")

    def _report_client_statement(self):
        """Client financial statement - pick client first."""
        dlg = QDialog(self)
        dlg.setWindowTitle("اختر العميل")
        dlg.setLayoutDirection(Qt.RightToLeft)
        dlg.setFixedWidth(400)
        layout = QVBoxLayout(dlg)
        lbl = QLabel("اختر العميل لعرض كشف حسابه:")
        lbl.setObjectName("form_label")
        combo = QComboBox()
        combo.setLayoutDirection(Qt.RightToLeft)
        clients = db.get_clients()
        for c in clients:
            combo.addItem(f"{c['code']} - {c['name']}", c["id"])
        btn_row = QHBoxLayout()
        ok_btn = make_btn("عرض التقرير", "primary")
        ok_btn.clicked.connect(dlg.accept)
        cancel_btn = make_btn("إلغاء", "secondary")
        cancel_btn.clicked.connect(dlg.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(ok_btn)
        layout.addWidget(lbl)
        layout.addWidget(combo)
        layout.addLayout(btn_row)

        if dlg.exec_() == QDialog.Accepted:
            client_id = combo.currentData()
            client_name = combo.currentText()
            self._generate_client_statement(client_id, client_name)

    def _generate_client_statement(self, client_id, client_name):
        office, sub = self._get_office()
        fees = db.get_fees(client_id=client_id)
        cases = db.get_cases(client_id=client_id)

        fee_rows = [[f.get("case_code",""), f"{f.get('total_fees',0):,.2f}",
                     f"{f.get('paid',0):,.2f}", f"{f.get('remaining',0):,.2f}",
                     f.get("payment_date","")]
                    for f in fees]
        total = sum(f.get("total_fees",0) for f in fees)
        paid = sum(f.get("paid",0) for f in fees)
        remaining = sum(f.get("remaining",0) for f in fees)

        html = build_html_report(
            f"كشف حساب العميل: {client_name}", office, sub,
            fee_rows,
            ["تاريخ آخر دفعة", "المتبقي (ج.م)", "المدفوع (ج.م)", "الإجمالي (ج.م)", "القضية"],
            f"إجمالي الأتعاب: {total:,.2f} ج.م | المدفوع: {paid:,.2f} ج.م | المتبقي: {remaining:,.2f} ج.م"
        )
        self._show_report(html, f"كشف حساب - {client_name}")
