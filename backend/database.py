# backend/database.py
# Compatibility shim: use the SQLite wrapper we created (auth_database.py)
# so existing auth services that expect get_db_connection() continue to work.

from auth_database import get_db_connection

# Provide the same name used in the auth services
__all__ = ["get_db_connection"]
