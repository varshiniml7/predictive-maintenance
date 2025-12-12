import sqlite3

conn = sqlite3.connect("auth.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS otp_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    otp TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()

print("OTP table created successfully.")
