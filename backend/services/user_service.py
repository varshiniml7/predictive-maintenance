import bcrypt
import pymysql
from datetime import datetime
from config import Config
from database import get_db_connection

def hash_password(password):
    """Hash the password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed_password):
    """Verify password"""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def create_user(name, email, password):
    """Create a new user"""
    hashed = hash_password(password)
    created_at = datetime.utcnow()

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO users (name, email, password_hash, created_at)
                VALUES (%s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (name, email, hashed, created_at))
                conn.commit()
            except pymysql.err.IntegrityError:
                raise ValueError("Email already exists")

    return {
        "name": name,
        "email": email,
        "created_at": created_at.isoformat()
    }

def authenticate_user(email, password):
    """Authenticate the user"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT id, name, email, password_hash FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if not user:
                return None

            if not check_password(password, user["password_hash"]):
                return None

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }

def get_user_by_email(email):
    """Get user by email"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT id, name, email FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            return cursor.fetchone()

def update_user_password(email, new_password):
    """Update user password"""
    hashed = hash_password(new_password)

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = "UPDATE users SET password_hash = %s WHERE email = %s"
            cursor.execute(sql, (hashed, email))
            conn.commit()
