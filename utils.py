import psycopg2 as ps2
from pydantic import BaseModel
from typing import Optional
import hashlib

class User(BaseModel):
    id: int
    username: str
    hashed_password: str
    email: Optional[str] = None
    is_admin: Optional[bool] = None
    is_premium: Optional[bool] = None
    qr_count: Optional[int] = None
    qr_changes: Optional[int] = None

def get_user_by_username(username:str, db_info:str):
    """
    Returns User object if user is found. Otherwise returns None
    """
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM users WHERE username='{username}';")
            cur_return = cur.fetchone()
            if not cur_return: # No user found
                return None
            return User(**dict(zip(['id', 'username', 'hashed_password', 'email', 'is_admin', 'is_premium', 'qr_count', 'qr_changes'], cur_return)))
            
def hash_sha256(string:str) -> str:
    m = hashlib.sha256(string.encode())
    return m.hexdigest()
