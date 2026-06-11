import sqlite3
import json

DB_NAME = "forms.db"


# ----------------------------
# Connection
# ----------------------------
def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------
# Initialize Database
# ----------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Forms Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS forms (
        form_id TEXT PRIMARY KEY,
        form_name TEXT,
        columns TEXT,
        created_at TEXT
    )
    """)

    # Recipients Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recipients (
        recipient_id TEXT PRIMARY KEY,
        form_id TEXT,
        email TEXT,
        status TEXT DEFAULT 'Pending'
    )
    """)

    # Responses Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        response_id TEXT PRIMARY KEY,
        form_id TEXT,
        response_data TEXT,
        submitted_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# ----------------------------
# Forms
# ----------------------------
def create_form(form_id, form_name, columns, created_at):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO forms
    (form_id, form_name, columns, created_at)
    VALUES (?, ?, ?, ?)
    """, (
        form_id,
        form_name,
        json.dumps(columns),
        created_at
    ))

    conn.commit()
    conn.close()


def get_forms():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM forms")

    rows = cur.fetchall()

    conn.close()
    return rows


def get_form(form_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM forms WHERE form_id=?",
        (form_id,)
    )

    row = cur.fetchone()

    conn.close()
    return row


def delete_form(form_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM forms WHERE form_id=?",
        (form_id,)
    )

    conn.commit()
    conn.close()


# ----------------------------
# Recipients
# ----------------------------
def add_recipient(
    recipient_id,
    form_id,
    email
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO recipients
    (recipient_id, form_id, email)
    VALUES (?, ?, ?)
    """, (
        recipient_id,
        form_id,
        email
    ))

    conn.commit()
    conn.close()


def get_recipients(form_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM recipients WHERE form_id=?",
        (form_id,)
    )

    rows = cur.fetchall()

    conn.close()
    return rows


def update_recipient_status(
    email,
    form_id,
    status
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE recipients
    SET status=?
    WHERE email=? AND form_id=?
    """, (
        status,
        email,
        form_id
    ))

    conn.commit()
    conn.close()


# ----------------------------
# Responses
# ----------------------------
def save_response(
    response_id,
    form_id,
    response_data,
    submitted_at
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO responses
    (
        response_id,
        form_id,
        response_data,
        submitted_at
    )
    VALUES (?, ?, ?, ?)
    """, (
        response_id,
        form_id,
        json.dumps(response_data),
        submitted_at
    ))

    conn.commit()
    conn.close()


def get_responses():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM responses ORDER BY submitted_at DESC"
    )

    rows = cur.fetchall()

    conn.close()
    return rows


def get_form_responses(form_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM responses WHERE form_id=?",
        (form_id,)
    )

    rows = cur.fetchall()

    conn.close()
    return rows


def delete_response(response_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM responses WHERE response_id=?",
        (response_id,)
    )

    conn.commit()
    conn.close()


# ----------------------------
# Dashboard Stats
# ----------------------------
def get_stats(form_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM recipients WHERE form_id=?",
        (form_id,)
    )
    total = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM recipients WHERE form_id=? AND status='Submitted'",
        (form_id,)
    )
    submitted = cur.fetchone()[0]

    pending = total - submitted

    conn.close()

    return {
        "total": total,
        "submitted": submitted,
        "pending": pending
    }
