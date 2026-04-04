import sqlite3
from datetime import datetime

DB_PATH = "katalot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            message   TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_message(text):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO messages (message, created_at) VALUES (?, ?)",
        (text, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    print(f"✅ Inserted: {text}")

if __name__ == "__main__":
    init_db()
    insert_message("Hello World!")
    insert_message(f"Run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
