# import sqlite3
# import json
# from datetime import datetime

# DB_PATH = "quiz_rt.db"

# def _conn():
#     return sqlite3.connect(DB_PATH, check_same_thread=False)

# def init_db():
#     con = _conn()
#     c = con.cursor()

#     c.execute("""
#     CREATE TABLE IF NOT EXISTS candidates (
#         token TEXT PRIMARY KEY,
#         name TEXT,
#         email TEXT,
#         domain TEXT,
#         created_at TEXT
#     )""")

#     c.execute("""
#     CREATE TABLE IF NOT EXISTS quizzes (
#         token TEXT PRIMARY KEY,
#         quiz_json TEXT,
#         created_at TEXT
#     )""")

#     c.execute("""
#     CREATE TABLE IF NOT EXISTS results (
#         token TEXT PRIMARY KEY,
#         name TEXT,
#         email TEXT,
#         domain TEXT,
#         score INTEGER,
#         details_json TEXT,
#         submitted_at TEXT
#     )""")
#     con.commit()
#     con.close()

# def save_candidate(token, name, email, domain):
#     con = _conn()
#     c = con.cursor()
#     c.execute("REPLACE INTO candidates VALUES (?, ?, ?, ?, ?)",
#               (token, name, email, domain, datetime.now().isoformat()))
#     con.commit()
#     con.close()

# def get_candidate(token):
#     con = _conn()
#     c = con.cursor()
#     c.execute("SELECT token, name, email, domain, created_at FROM candidates WHERE token=?", (token,))
#     row = c.fetchone()
#     con.close()
#     return row

# def save_quiz(token, quiz_list):
#     con = _conn()
#     c = con.cursor()
#     c.execute("REPLACE INTO quizzes VALUES (?, ?, ?)",
#               (token, json.dumps(quiz_list), datetime.now().isoformat()))
#     con.commit()
#     con.close()

# def get_quiz(token):
#     con = _conn()
#     c = con.cursor()
#     c.execute("SELECT quiz_json FROM quizzes WHERE token=?", (token,))
#     row = c.fetchone()
#     con.close()
#     if not row:
#         return None
#     return json.loads(row[0])

# def save_result(token, name, email, domain, score, details):
#     con = _conn()
#     c = con.cursor()
#     c.execute("REPLACE INTO results VALUES (?, ?, ?, ?, ?, ?, ?)",
#               (token, name, email, domain, score, json.dumps(details), datetime.now().isoformat()))
#     con.commit()
#     con.close()

# def get_results_joined():
#     """Return rows for HR table"""
#     con = _conn()
#     c = con.cursor()
#     c.execute("""
#     SELECT r.token, r.name, r.email, r.domain, r.score, r.details_json, r.submitted_at
#     FROM results r
#     ORDER BY r.submitted_at DESC
#     """)
#     rows = c.fetchall()
#     con.close()
#     return rows

















import sqlite3
from datetime import datetime

DB_NAME = "quiz_system.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Candidates table
    c.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            token TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            domain TEXT
        )
    """)
    
    # Results table
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            token TEXT,
            name TEXT,
            email TEXT,
            domain TEXT,
            score INTEGER,
            datetime TEXT,
            PRIMARY KEY(token)
        )
    """)
    
    conn.commit()
    conn.close()

# ---------- Candidate Functions ----------
def save_candidate(token, name, email, domain):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "REPLACE INTO candidates (token, name, email, domain) VALUES (?, ?, ?, ?)",
        (token, name, email, domain)
    )
    conn.commit()
    conn.close()

def get_candidate(token):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM candidates WHERE token=?", (token,))
    row = c.fetchone()
    conn.close()
    return row

# ---------- Results Functions ----------
def save_result(token, name, email, score, details=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    domain = ""
    # Try fetching domain
    c.execute("SELECT domain FROM candidates WHERE token=?", (token,))
    row = c.fetchone()
    if row:
        domain = row[0]
    c.execute(
        "REPLACE INTO results (token, name, email, domain, score, datetime) VALUES (?, ?, ?, ?, ?, ?)",
        (token, name, email, domain, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_results():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM results ORDER BY datetime DESC")
    rows = c.fetchall()
    conn.close()
    return rows
