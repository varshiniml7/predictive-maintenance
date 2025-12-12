import jwt
from datetime import datetime, timedelta
from config import Config

def generate_token(user):
    """
    Generate a JWT token for a user.
    Expected user dict: { "id": ..., "name": ..., "email": ... }
    """
    payload = {
        "id": user.get("id"),
        "name": user.get("name"),
        "email": user.get("email"),
        "exp": datetime.utcnow() + timedelta(seconds=Config.JWT_EXPIRES_IN)
    }

    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")
    return token
