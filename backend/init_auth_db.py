# backend/init_auth_db.py
from auth_database import get_db_connection

CREATE_USERS_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at DATETIME DEFAULT (datetime('now'))
);
"""

CREATE_OTPS_SQL = """
CREATE TABLE IF NOT EXISTS otp_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  otp TEXT NOT NULL,
  expires_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT (datetime('now'))
);
"""

def main():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(CREATE_USERS_SQL)
        cur.execute(CREATE_OTPS_SQL)
        print("Auth DB initialized successfully.")

if __name__ == "__main__":
    main()
