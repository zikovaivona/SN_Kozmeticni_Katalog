import getpass
import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sephora.db")

def main():
    username = input("Admin username: ").strip()
    password = getpass.getpass("Admin password (min 6 characters): ")

    if len(username) < 3 or len(password) < 6:
        raise SystemExit("Username must have at least 3 characters and password at least 6 characters.")

    db = sqlite3.connect(DB_PATH)
    columns = [row[1] for row in db.execute("PRAGMA table_info(users)").fetchall()]

    if not columns:
        db.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    elif "role" not in columns:
        db.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")

    existing = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if existing:
        db.execute(
            "UPDATE users SET password_hash=?, role='admin' WHERE id=?",
            (generate_password_hash(password), existing[0])
        )
        print(f"Updated {username!r} to administrator.")
    else:
        db.execute(
            "INSERT INTO users(username,password_hash,role) VALUES (?,?,?)",
            (username, generate_password_hash(password), "admin")
        )
        print(f"Created administrator {username!r}.")

    db.commit()
    db.close()

if __name__ == "__main__":
    main()
