# backend/services/otp_service.py
import random
import hashlib
from datetime import datetime, timedelta
from database import get_db_connection
from config import Config

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def hash_otp(otp):
    """Hash OTP using SHA-256 for secure storage"""
    return hashlib.sha256(otp.encode()).hexdigest()

def create_otp_request(email):
    """Create and store an OTP entry for the user"""
    otp = generate_otp()
    hashed = hash_otp(otp)
    expires_at = datetime.utcnow() + timedelta(minutes=Config.OTP_EXPIRATION_MINUTES)

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO otp_requests (email, otp, expires_at)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (email, hashed, expires_at))
            conn.commit()

    return otp, expires_at

def verify_otp(email, otp):
    """Verify whether the provided OTP is valid and not expired"""
    hashed = hash_otp(otp)

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = """
            SELECT id, expires_at FROM otp_requests
            WHERE email = %s AND otp = %s
            ORDER BY id DESC LIMIT 1
            """
            cursor.execute(sql, (email, hashed))
            record = cursor.fetchone()

            if not record:
                return False, "Invalid OTP"

            expires_at = record["expires_at"]

            # if expires_at is stored as text, convert to datetime if needed
            if isinstance(expires_at, str):
                try:
                    # try parsing common SQLite datetime format
                    expires_at_dt = datetime.fromisoformat(expires_at)
                except Exception:
                    # fallback: treat as not expired
                    expires_at_dt = expires_at
            else:
                expires_at_dt = expires_at

            if isinstance(expires_at_dt, datetime) and datetime.utcnow() > expires_at_dt:
                return False, "OTP has expired"

    return True, "OTP verified"

def clear_otps(email):
    """Remove all OTP records for the given email"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = "DELETE FROM otp_requests WHERE email = %s"
            cursor.execute(sql, (email,))
            conn.commit()
