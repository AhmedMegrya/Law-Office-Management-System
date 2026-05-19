"""
database.py - SQLite Database Manager for Law Office Management System
"""
import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "law_office.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_database():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        role TEXT DEFAULT 'viewer',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )""")

    # Settings table
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")

    # Clients table
    c.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        name TEXT NOT NULL,
        phone TEXT,
        whatsapp TEXT,
        national_id TEXT,
        address TEXT,
        email TEXT,
        client_type TEXT DEFAULT 'فرد',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Cases table
    c.execute("""CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        client_id INTEGER,
        client_role TEXT,
        case_type TEXT,
        case_number TEXT,
        case_year TEXT,
        court TEXT,
        circuit TEXT,
        opponent TEXT,
        opponent_lawyer TEXT,
        subject TEXT,
        requests TEXT,
        last_action TEXT,
        status TEXT DEFAULT 'متداولة',
        file_open_date TEXT,
        last_update TEXT DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        archive_path TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )""")

    # Sessions table
    c.execute("""CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER,
        session_date TEXT,
        session_time TEXT,
        court TEXT,
        circuit TEXT,
        previous_decision TEXT,
        required_action TEXT,
        result TEXT,
        notes TEXT,
        status TEXT DEFAULT 'قادمة',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    )""")

    # Fees table
    c.execute("""CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER,
        client_id INTEGER,
        total_fees REAL DEFAULT 0,
        paid REAL DEFAULT 0,
        remaining REAL DEFAULT 0,
        payment_method TEXT,
        payment_date TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(case_id) REFERENCES cases(id),
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )""")

    # Payments table
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fee_id INTEGER,
        case_id INTEGER,
        client_id INTEGER,
        amount REAL,
        payment_method TEXT,
        payment_date TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(fee_id) REFERENCES fees(id)
    )""")

    # Expenses table
    c.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER,
        expense_type TEXT,
        amount REAL,
        expense_date TEXT,
        description TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    )""")

    # Documents / Archive table
    c.execute("""CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER,
        client_id INTEGER,
        doc_type TEXT,
        file_name TEXT,
        file_path TEXT,
        description TEXT,
        added_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(case_id) REFERENCES cases(id),
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )""")

    # Powers of Attorney table
    c.execute("""CREATE TABLE IF NOT EXISTS powers_of_attorney (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poa_number TEXT,
        poa_letter TEXT,
        poa_year TEXT,
        notary_office TEXT,
        client_id INTEGER,
        attorney_name TEXT,
        poa_type TEXT,
        poa_date TEXT,
        expiry_date TEXT,
        notes TEXT,
        file_path TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )""")

    # Insert default admin user
    admin_pass = hash_password("admin123")
    c.execute("""INSERT OR IGNORE INTO users (username, password, full_name, role)
                 VALUES (?, ?, ?, ?)""",
              ("admin", admin_pass, "المدير العام", "admin"))

    # Insert default employee user
    emp_pass = hash_password("emp123")
    c.execute("""INSERT OR IGNORE INTO users (username, password, full_name, role)
                 VALUES (?, ?, ?, ?)""",
              ("employee", emp_pass, "موظف المكتب", "employee"))

    # Insert default settings
    default_settings = {
        "office_name": "مكتب المستشار/ أحمد شعبان مجرية",
        "office_subtitle": "للمحاماة والاستشارات القانونية",
        "lawyer_name": "المستشار/ أحمد شعبان مجرية",
        "phone": "",
        "address": "",
        "alert_days": "3",
        "archive_path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "Archive"),
        "backup_path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "Backups"),
    }
    for key, value in default_settings.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def get_setting(key, default=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def authenticate_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    hashed = hash_password(password)
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND is_active=1",
              (username, hashed))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None


def get_next_client_code():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM clients")
    cnt = c.fetchone()["cnt"]
    conn.close()
    return f"CL{cnt + 1:04d}"


def get_next_case_code():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM cases")
    cnt = c.fetchone()["cnt"]
    conn.close()
    return f"CS{cnt + 1:04d}"


# ─── Dashboard Stats ────────────────────────────────────────────────
def get_dashboard_stats():
    conn = get_connection()
    c = conn.cursor()
    stats = {}

    c.execute("SELECT COUNT(*) as cnt FROM clients")
    stats["clients"] = c.fetchone()["cnt"]

    c.execute("SELECT COUNT(*) as cnt FROM cases")
    stats["cases"] = c.fetchone()["cnt"]

    c.execute("SELECT COUNT(*) as cnt FROM cases WHERE status='متداولة'")
    stats["active_cases"] = c.fetchone()["cnt"]

    c.execute("SELECT COUNT(*) as cnt FROM sessions WHERE status='قادمة' AND session_date >= date('now')")
    stats["upcoming_sessions"] = c.fetchone()["cnt"]

    c.execute("SELECT COALESCE(SUM(total_fees),0) as t FROM fees")
    stats["total_fees"] = c.fetchone()["t"]

    c.execute("SELECT COALESCE(SUM(paid),0) as t FROM fees")
    stats["total_paid"] = c.fetchone()["t"]

    c.execute("SELECT COALESCE(SUM(remaining),0) as t FROM fees")
    stats["total_remaining"] = c.fetchone()["t"]

    # Upcoming sessions (next N days)
    alert_days = int(get_setting("alert_days", "3"))
    c.execute("""SELECT s.*, ca.code as case_code, ca.case_number, cl.name as client_name
                 FROM sessions s
                 JOIN cases ca ON s.case_id = ca.id
                 JOIN clients cl ON ca.client_id = cl.id
                 WHERE s.status='قادمة'
                 AND s.session_date BETWEEN date('now') AND date('now', '+' || ? || ' days')
                 ORDER BY s.session_date""", (alert_days,))
    stats["alerts"] = [dict(r) for r in c.fetchall()]

    # Last 5 cases
    c.execute("""SELECT ca.*, cl.name as client_name
                 FROM cases ca JOIN clients cl ON ca.client_id = cl.id
                 ORDER BY ca.id DESC LIMIT 5""")
    stats["recent_cases"] = [dict(r) for r in c.fetchall()]

    conn.close()
    return stats


# ─── Clients CRUD ───────────────────────────────────────────────────
def add_client(data):
    conn = get_connection()
    c = conn.cursor()
    code = get_next_client_code()
    c.execute("""INSERT INTO clients (code,name,phone,whatsapp,national_id,address,email,client_type,notes)
                 VALUES (?,?,?,?,?,?,?,?,?)""",
              (code, data["name"], data.get("phone",""), data.get("whatsapp",""),
               data.get("national_id",""), data.get("address",""), data.get("email",""),
               data.get("client_type","فرد"), data.get("notes","")))
    conn.commit()
    cid = c.lastrowid
    conn.close()
    return cid


def update_client(cid, data):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""UPDATE clients SET name=?,phone=?,whatsapp=?,national_id=?,
                 address=?,email=?,client_type=?,notes=? WHERE id=?""",
              (data["name"], data.get("phone",""), data.get("whatsapp",""),
               data.get("national_id",""), data.get("address",""), data.get("email",""),
               data.get("client_type","فرد"), data.get("notes",""), cid))
    conn.commit()
    conn.close()


def delete_client(cid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM clients WHERE id=?", (cid,))
    conn.commit()
    conn.close()


def get_clients(search=""):
    conn = get_connection()
    c = conn.cursor()
    if search:
        q = f"%{search}%"
        c.execute("""SELECT * FROM clients WHERE name LIKE ? OR phone LIKE ? OR code LIKE ?
                     OR national_id LIKE ? ORDER BY id DESC""", (q,q,q,q))
    else:
        c.execute("SELECT * FROM clients ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_client(cid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM clients WHERE id=?", (cid,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Cases CRUD ─────────────────────────────────────────────────────
def add_case(data):
    conn = get_connection()
    c = conn.cursor()
    code = get_next_case_code()
    today = datetime.now().strftime("%Y-%m-%d")

    # Create archive folder
    client = get_client(data["client_id"])
    # Sanitize client name for folder: keep only alphanumeric and underscore
    import re
    def sanitize_folder_name(name):
        # Remove non-alphanumeric characters but keep Arabic letters
        return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
    
    client_name = sanitize_folder_name(client["name"]) if client else "unknown"
    folder_name = f"{code}_{client_name}_{data.get('case_number','')}_{data.get('case_year','')}"
    archive_base = get_setting("archive_path",
                               os.path.join(os.path.dirname(os.path.abspath(__file__)), "Archive"))
    case_folder = os.path.join(archive_base, folder_name)
    subfolders = ["01_Powers", "02_Contracts", "03_Lawsuits",
                  "04_Memos", "05_Portfolios", "06_Judgments",
                  "07_Reports", "08_Documents", "09_Others"]
    os.makedirs(case_folder, exist_ok=True)
    for sf in subfolders:
        os.makedirs(os.path.join(case_folder, sf), exist_ok=True)

    c.execute("""INSERT INTO cases
                 (code,client_id,client_role,case_type,case_number,case_year,court,circuit,
                  opponent,opponent_lawyer,subject,requests,last_action,status,
                  file_open_date,last_update,notes,archive_path)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (code, data["client_id"], data.get("client_role",""),
               data.get("case_type","مدني"), data.get("case_number",""),
               data.get("case_year",""), data.get("court",""), data.get("circuit",""),
               data.get("opponent",""), data.get("opponent_lawyer",""),
               data.get("subject",""), data.get("requests",""),
               data.get("last_action",""), data.get("status","متداولة"),
               data.get("file_open_date", today), today,
               data.get("notes",""), case_folder))
    conn.commit()
    case_id = c.lastrowid
    conn.close()
    return case_id


def update_case(case_id, data):
    conn = get_connection()
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("""UPDATE cases SET client_id=?,client_role=?,case_type=?,case_number=?,case_year=?,
                 court=?,circuit=?,opponent=?,opponent_lawyer=?,subject=?,requests=?,
                 last_action=?,status=?,file_open_date=?,last_update=?,notes=? WHERE id=?""",
              (data["client_id"], data.get("client_role",""), data.get("case_type","مدني"),
               data.get("case_number",""), data.get("case_year",""), data.get("court",""),
               data.get("circuit",""), data.get("opponent",""), data.get("opponent_lawyer",""),
               data.get("subject",""), data.get("requests",""), data.get("last_action",""),
               data.get("status","متداولة"), data.get("file_open_date",""), today,
               data.get("notes",""), case_id))
    conn.commit()
    conn.close()


def delete_case(case_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM cases WHERE id=?", (case_id,))
    conn.commit()
    conn.close()


def get_cases(search="", status="", case_type="", court="", client_id=None):
    conn = get_connection()
    c = conn.cursor()
    query = """SELECT ca.*, cl.name as client_name
               FROM cases ca JOIN clients cl ON ca.client_id = cl.id WHERE 1=1"""
    params = []
    if search:
        query += " AND (ca.code LIKE ? OR ca.case_number LIKE ? OR cl.name LIKE ? OR ca.subject LIKE ?)"
        q = f"%{search}%"
        params += [q,q,q,q]
    if status:
        query += " AND ca.status=?"
        params.append(status)
    if case_type:
        query += " AND ca.case_type=?"
        params.append(case_type)
    if court:
        query += " AND ca.court LIKE ?"
        params.append(f"%{court}%")
    if client_id:
        query += " AND ca.client_id=?"
        params.append(client_id)
    query += " ORDER BY ca.id DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_case(case_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT ca.*, cl.name as client_name
                 FROM cases ca JOIN clients cl ON ca.client_id=cl.id WHERE ca.id=?""", (case_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Sessions CRUD ──────────────────────────────────────────────────
def add_session(data):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO sessions
                 (case_id,session_date,session_time,court,circuit,previous_decision,
                  required_action,result,notes,status)
                 VALUES (?,?,?,?,?,?,?,?,?,?)""",
              (data["case_id"], data.get("session_date",""), data.get("session_time",""),
               data.get("court",""), data.get("circuit",""),
               data.get("previous_decision",""), data.get("required_action",""),
               data.get("result",""), data.get("notes",""), data.get("status","قادمة")))
    conn.commit()
    sid = c.lastrowid
    conn.close()
    return sid


def update_session(sid, data):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""UPDATE sessions SET session_date=?,session_time=?,court=?,circuit=?,
                 previous_decision=?,required_action=?,result=?,notes=?,status=? WHERE id=?""",
              (data.get("session_date",""), data.get("session_time",""),
               data.get("court",""), data.get("circuit",""),
               data.get("previous_decision",""), data.get("required_action",""),
               data.get("result",""), data.get("notes",""),
               data.get("status","قادمة"), sid))
    conn.commit()
    conn.close()


def delete_session(sid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE id=?", (sid,))
    conn.commit()
    conn.close()


def get_sessions(case_id=None, date_filter=None, status=None):
    conn = get_connection()
    c = conn.cursor()
    query = """SELECT s.*, ca.code as case_code, ca.case_number, ca.court as case_court,
                      cl.name as client_name, ca.case_type
               FROM sessions s
               JOIN cases ca ON s.case_id = ca.id
               JOIN clients cl ON ca.client_id = cl.id
               WHERE 1=1"""
    params = []
    if case_id:
        query += " AND s.case_id=?"
        params.append(case_id)
    if date_filter == "today":
        query += " AND s.session_date = date('now')"
    elif date_filter == "week":
        query += " AND s.session_date BETWEEN date('now') AND date('now','+7 days')"
    elif date_filter == "upcoming":
        query += " AND s.session_date >= date('now')"
    if status:
        query += " AND s.status=?"
        params.append(status)
    query += " ORDER BY s.session_date, s.session_time"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ─── Fees CRUD ──────────────────────────────────────────────────────
def add_fee(data):
    conn = get_connection()
    c = conn.cursor()
    remaining = float(data.get("total_fees",0)) - float(data.get("paid",0))
    c.execute("""INSERT INTO fees (case_id,client_id,total_fees,paid,remaining,
                 payment_method,payment_date,notes)
                 VALUES (?,?,?,?,?,?,?,?)""",
              (data.get("case_id"), data.get("client_id"),
               data.get("total_fees",0), data.get("paid",0), remaining,
               data.get("payment_method",""), data.get("payment_date",""),
               data.get("notes","")))
    conn.commit()
    fid = c.lastrowid
    conn.close()
    return fid


def add_payment(data):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO payments (fee_id,case_id,client_id,amount,payment_method,payment_date,notes)
                 VALUES (?,?,?,?,?,?,?)""",
              (data.get("fee_id"), data.get("case_id"), data.get("client_id"),
               data.get("amount",0), data.get("payment_method",""),
               data.get("payment_date",""), data.get("notes","")))
    # Update fee record
    if data.get("fee_id"):
        c.execute("SELECT * FROM fees WHERE id=?", (data["fee_id"],))
        fee = c.fetchone()
        if fee:
            new_paid = fee["paid"] + float(data.get("amount",0))
            new_remaining = fee["total_fees"] - new_paid
            c.execute("UPDATE fees SET paid=?, remaining=? WHERE id=?",
                      (new_paid, new_remaining, data["fee_id"]))
    conn.commit()
    conn.close()


def get_fees(client_id=None, case_id=None):
    conn = get_connection()
    c = conn.cursor()
    query = """SELECT f.*, cl.name as client_name, ca.code as case_code, ca.case_number
               FROM fees f
               LEFT JOIN clients cl ON f.client_id=cl.id
               LEFT JOIN cases ca ON f.case_id=ca.id
               WHERE 1=1"""
    params = []
    if client_id:
        query += " AND f.client_id=?"
        params.append(client_id)
    if case_id:
        query += " AND f.case_id=?"
        params.append(case_id)
    query += " ORDER BY f.id DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ─── Expenses CRUD ──────────────────────────────────────────────────
def add_expense(data):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO expenses (case_id,expense_type,amount,expense_date,description,notes)
                 VALUES (?,?,?,?,?,?)""",
              (data.get("case_id"), data.get("expense_type",""),
               data.get("amount",0), data.get("expense_date",""),
               data.get("description",""), data.get("notes","")))
    conn.commit()
    eid = c.lastrowid
    conn.close()
    return eid


def update_expense(eid, data):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""UPDATE expenses SET case_id=?,expense_type=?,amount=?,expense_date=?,
                 description=?,notes=? WHERE id=?""",
              (data.get("case_id"), data.get("expense_type",""),
               data.get("amount",0), data.get("expense_date",""),
               data.get("description",""), data.get("notes",""), eid))
    conn.commit()
    conn.close()


def delete_expense(eid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (eid,))
    conn.commit()
    conn.close()


def get_expenses(case_id=None, month=None):
    conn = get_connection()
    c = conn.cursor()
    query = """SELECT e.*, ca.code as case_code, ca.case_number
               FROM expenses e LEFT JOIN cases ca ON e.case_id=ca.id WHERE 1=1"""
    params = []
    if case_id:
        query += " AND e.case_id=?"
        params.append(case_id)
    if month:
        query += " AND strftime('%Y-%m', e.expense_date)=?"
        params.append(month)
    query += " ORDER BY e.expense_date DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ─── Documents CRUD ─────────────────────────────────────────────────
def add_document(data):
    conn = get_connection()
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("""INSERT INTO documents (case_id,client_id,doc_type,file_name,file_path,description,added_date)
                 VALUES (?,?,?,?,?,?,?)""",
              (data.get("case_id"), data.get("client_id"), data.get("doc_type","أخرى"),
               data.get("file_name",""), data.get("file_path",""),
               data.get("description",""), today))
    conn.commit()
    did = c.lastrowid
    conn.close()
    return did


def delete_document(did):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT file_path FROM documents WHERE id=?", (did,))
    row = c.fetchone()
    c.execute("DELETE FROM documents WHERE id=?", (did,))
    conn.commit()
    conn.close()
    return row["file_path"] if row else None


def get_documents(case_id=None, client_id=None, doc_type=None, search=""):
    conn = get_connection()
    c = conn.cursor()
    query = """SELECT d.*, cl.name as client_name, ca.code as case_code, ca.case_number
               FROM documents d
               LEFT JOIN clients cl ON d.client_id=cl.id
               LEFT JOIN cases ca ON d.case_id=ca.id
               WHERE 1=1"""
    params = []
    if case_id:
        query += " AND d.case_id=?"
        params.append(case_id)
    if client_id:
        query += " AND d.client_id=?"
        params.append(client_id)
    if doc_type:
        query += " AND d.doc_type=?"
        params.append(doc_type)
    if search:
        q = f"%{search}%"
        query += " AND (d.file_name LIKE ? OR d.description LIKE ? OR cl.name LIKE ?)"
        params += [q, q, q]
    query += " ORDER BY d.id DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ─── Powers of Attorney CRUD ────────────────────────────────────────
def add_poa(data):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO powers_of_attorney
                 (poa_number,poa_letter,poa_year,notary_office,client_id,attorney_name,
                  poa_type,poa_date,expiry_date,notes,file_path)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (data.get("poa_number",""), data.get("poa_letter",""),
               data.get("poa_year",""), data.get("notary_office",""),
               data.get("client_id"), data.get("attorney_name",""),
               data.get("poa_type","عام قضايا"), data.get("poa_date",""),
               data.get("expiry_date",""), data.get("notes",""),
               data.get("file_path","")))
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid


def update_poa(pid, data):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""UPDATE powers_of_attorney SET poa_number=?,poa_letter=?,poa_year=?,
                 notary_office=?,client_id=?,attorney_name=?,poa_type=?,poa_date=?,
                 expiry_date=?,notes=?,file_path=? WHERE id=?""",
              (data.get("poa_number",""), data.get("poa_letter",""),
               data.get("poa_year",""), data.get("notary_office",""),
               data.get("client_id"), data.get("attorney_name",""),
               data.get("poa_type",""), data.get("poa_date",""),
               data.get("expiry_date",""), data.get("notes",""),
               data.get("file_path",""), pid))
    conn.commit()
    conn.close()


def delete_poa(pid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM powers_of_attorney WHERE id=?", (pid,))
    conn.commit()
    conn.close()


def get_poas(search="", client_id=None):
    conn = get_connection()
    c = conn.cursor()
    query = """SELECT p.*, cl.name as client_name
               FROM powers_of_attorney p
               LEFT JOIN clients cl ON p.client_id=cl.id
               WHERE 1=1"""
    params = []
    if search:
        q = f"%{search}%"
        query += " AND (p.poa_number LIKE ? OR cl.name LIKE ? OR p.attorney_name LIKE ?)"
        params += [q, q, q]
    if client_id:
        query += " AND p.client_id=?"
        params.append(client_id)
    query += " ORDER BY p.id DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ─── Users CRUD ─────────────────────────────────────────────────────
def get_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id,username,full_name,role,is_active,created_at FROM users ORDER BY id")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_user(data):
    conn = get_connection()
    c = conn.cursor()
    hashed = hash_password(data["password"])
    c.execute("""INSERT INTO users (username,password,full_name,role)
                 VALUES (?,?,?,?)""",
              (data["username"], hashed, data.get("full_name",""), data.get("role","viewer")))
    conn.commit()
    conn.close()


def update_user(uid, data):
    conn = get_connection()
    c = conn.cursor()
    if data.get("password"):
        hashed = hash_password(data["password"])
        c.execute("""UPDATE users SET full_name=?,role=?,is_active=?,password=? WHERE id=?""",
                  (data.get("full_name",""), data.get("role","viewer"),
                   data.get("is_active",1), hashed, uid))
    else:
        c.execute("""UPDATE users SET full_name=?,role=?,is_active=? WHERE id=?""",
                  (data.get("full_name",""), data.get("role","viewer"),
                   data.get("is_active",1), uid))
    conn.commit()
    conn.close()


def delete_user(uid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit()
    conn.close()


# Global search
def global_search(query):
    conn = get_connection()
    c = conn.cursor()
    q = f"%{query}%"
    results = []

    c.execute("SELECT id,'client' as type, name as title, phone as detail FROM clients WHERE name LIKE ? OR phone LIKE ? OR code LIKE ?", (q,q,q))
    for r in c.fetchall():
        results.append(dict(r))

    c.execute("""SELECT ca.id,'case' as type, ca.code as title, ca.case_number||' - '||cl.name as detail
                 FROM cases ca JOIN clients cl ON ca.client_id=cl.id
                 WHERE ca.code LIKE ? OR ca.case_number LIKE ? OR ca.subject LIKE ? OR cl.name LIKE ?""", (q,q,q,q))
    for r in c.fetchall():
        results.append(dict(r))

    c.execute("""SELECT p.id,'poa' as type, p.poa_number as title, cl.name as detail
                 FROM powers_of_attorney p LEFT JOIN clients cl ON p.client_id=cl.id
                 WHERE p.poa_number LIKE ? OR cl.name LIKE ? OR p.attorney_name LIKE ?""", (q,q,q))
    for r in c.fetchall():
        results.append(dict(r))

    conn.close()
    return results


if __name__ == "__main__":
    init_database()
    print("DB ready:", DB_PATH)
