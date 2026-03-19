import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

# Store DB at backend/novamind.db reliably
BASE_DIR = Path(__file__).resolve().parents[2]  # -> backend/
DB_PATH = str(BASE_DIR / "novamind.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id TEXT PRIMARY KEY,
        title TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        chat_id TEXT,
        role TEXT,
        content TEXT,
        timestamp TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS facts (
        id TEXT PRIMARY KEY,
        fact TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_msg(chat_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "INSERT OR IGNORE INTO chats (id, title, created_at) VALUES (?, ?, ?)",
        (chat_id, "Session", datetime.now().isoformat())
    )
    c.execute(
        "INSERT INTO messages VALUES (?, ?, ?, ?)",
        (chat_id, role, content, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

def get_history(chat_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY timestamp",
        (chat_id,)
    )
    rows = c.fetchall()
    conn.close()

    return [{"role": r[0], "content": r[1]} for r in rows]

def get_facts(limit: int = 5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT fact FROM facts ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()

    return [r[0] for r in rows]

def save_fact(text: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "INSERT INTO facts VALUES (?, ?, ?)",
        (str(uuid.uuid4()), text, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

init_db()
