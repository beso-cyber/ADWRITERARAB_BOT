import sqlite3
from datetime import datetime, timedelta

DB_NAME = "database.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        credits INTEGER DEFAULT 0,
        subscription INTEGER DEFAULT 0,
        expire_date TEXT
    )
    """)
    conn.commit()
    conn.close()


def add_user(user_id: int, credits: int = 5):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, credits, subscription) VALUES (?, ?, 0)",
        (user_id, credits),
    )
    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id, credits, subscription, expire_date FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_credits(user_id: int, new_credits: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET credits=? WHERE user_id=?", (new_credits, user_id))
    conn.commit()
    conn.close()


def activate_subscription(user_id: int, days: int = 30):
    expire = datetime.now() + timedelta(days=days)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET subscription=1, expire_date=? WHERE user_id=?",
        (expire.isoformat(), user_id),
    )
    conn.commit()
    conn.close()



def is_subscriber(user_id: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT subscription, expire_date FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return False

    sub, expire = row
    if sub != 1 or not expire:
        return False

    expire_date = datetime.fromisoformat(expire)
    return datetime.now() <= expire_date



def get_users_count() -> int:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_all_users() -> list[int]:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]
