"""
auth.py — Simple user authentication for foodieSense
Uses SQLite + SHA-256 password hashing (no external deps needed).
"""

import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "feedback.db")


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_auth_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL DEFAULT 0,
            food_name  TEXT,
            liked      INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add user_id column if it doesn't exist (migration for existing DBs)
    try:
        con.execute("ALTER TABLE feedback ADD COLUMN user_id INTEGER NOT NULL DEFAULT 0")
    except Exception:
        pass
    # Migration: richer feedback columns (star rating, tags, comment)
    for col, ddl in [("rating", "INTEGER"), ("tags", "TEXT"), ("comment", "TEXT")]:
        try:
            con.execute(f"ALTER TABLE feedback ADD COLUMN {col} {ddl}")
        except Exception:
            pass
    con.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            subtotal    INTEGER,
            delivery    INTEGER,
            total       INTEGER,
            name        TEXT,
            phone       TEXT,
            address     TEXT,
            payment     TEXT,
            status      TEXT DEFAULT 'Placed',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id  INTEGER NOT NULL,
            food_name TEXT,
            price     INTEGER,
            qty       INTEGER
        )
    """)
    con.commit()
    con.close()


def signup(username: str, password: str) -> dict:
    if not username.strip() or not password.strip():
        return {"ok": False, "msg": "Username and password required."}
    if len(password) < 4:
        return {"ok": False, "msg": "Password must be at least 4 characters."}
    try:
        con = sqlite3.connect(DB_PATH)
        con.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                    (username.strip().lower(), _hash(password)))
        con.commit()
        user_id = con.execute("SELECT id FROM users WHERE username=?",
                              (username.strip().lower(),)).fetchone()[0]
        con.close()
        return {"ok": True, "user_id": user_id, "username": username.strip().lower()}
    except sqlite3.IntegrityError:
        return {"ok": False, "msg": "Username already taken."}


def login(username: str, password: str) -> dict:
    con = sqlite3.connect(DB_PATH)
    row = con.execute(
        "SELECT id, username FROM users WHERE username=? AND password=?",
        (username.strip().lower(), _hash(password))
    ).fetchone()
    con.close()
    if row:
        return {"ok": True, "user_id": row[0], "username": row[1]}
    return {"ok": False, "msg": "Wrong username or password."}


def save_feedback(user_id: int, food_name: str, liked: bool,
                  rating: int = None, tags: str = "", comment: str = ""):
    """`liked` still drives the ML model; rating/tags/comment are extra detail."""
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT INTO feedback (user_id, food_name, liked, rating, tags, comment) "
        "VALUES (?,?,?,?,?,?)",
        (user_id, food_name, int(liked), rating, tags, comment)
    )
    con.commit()
    con.close()


def get_user_stats(user_id: int) -> tuple:
    con = sqlite3.connect(DB_PATH)
    r = con.execute(
        "SELECT COUNT(*), SUM(liked), COUNT(DISTINCT food_name) FROM feedback WHERE user_id=?",
        (user_id,)
    ).fetchone()
    con.close()
    return (r[0] or 0), (r[1] or 0), (r[2] or 0)


def get_user_feedback(user_id: int):
    """Returns DataFrame of this user's feedback."""
    import pandas as pd
    con = sqlite3.connect(DB_PATH)
    df  = pd.read_sql(
        "SELECT food_name, liked FROM feedback WHERE user_id=?",
        con, params=(user_id,)
    )
    con.close()
    return df


def get_feedback_history(user_id: int):
    """Full feedback history (newest first) for the My Feedback page."""
    import pandas as pd
    con = sqlite3.connect(DB_PATH)
    df  = pd.read_sql(
        "SELECT food_name, liked, rating, tags, comment, created_at "
        "FROM feedback WHERE user_id=? ORDER BY id DESC",
        con, params=(user_id,)
    )
    con.close()
    return df


# ── Orders ────────────────────────────────────────────────────────────────────
FREE_DELIVERY_ABOVE = 499
DELIVERY_FEE        = 30


def calc_totals(cart: dict):
    subtotal = sum(i["price"] * i["qty"] for i in cart.values())
    delivery = 0 if (subtotal == 0 or subtotal >= FREE_DELIVERY_ABOVE) else DELIVERY_FEE
    return subtotal, delivery, subtotal + delivery


def place_order(user_id: int, cart: dict, name: str, phone: str, address: str, payment: str) -> int:
    subtotal, delivery, total = calc_totals(cart)
    con = sqlite3.connect(DB_PATH)
    cur = con.execute(
        "INSERT INTO orders (user_id, subtotal, delivery, total, name, phone, address, payment) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (user_id, subtotal, delivery, total, name, phone, address, payment),
    )
    order_id = cur.lastrowid
    con.executemany(
        "INSERT INTO order_items (order_id, food_name, price, qty) VALUES (?,?,?,?)",
        [(order_id, n, i["price"], i["qty"]) for n, i in cart.items()],
    )
    con.commit()
    con.close()
    return order_id


def get_orders(user_id: int):
    """Returns a list of order dicts (newest first), each with an 'items' list."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    orders = [dict(r) for r in con.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (user_id,))]
    for o in orders:
        o["items"] = [dict(r) for r in con.execute(
            "SELECT food_name, price, qty FROM order_items WHERE order_id=?", (o["id"],))]
    con.close()
    return orders
