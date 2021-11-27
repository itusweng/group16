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

def get_user(key:str, val:str, db_info:str):
    """
    Uses the "key" argument to match the "val" argument in database
    Returns User object if user is found. Otherwise returns None
    """
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM users WHERE {key}='{val}';")
            cur_return = cur.fetchone()
            if not cur_return: # No user found
                return None
            return User(**dict(zip(['id', 'username', 'hashed_password', 'email', 'is_admin', 'is_premium', 'qr_count', 'qr_changes'], cur_return)))
            
def hash_sha256(string:str) -> str:
    m = hashlib.sha256(string.encode())
    return m.hexdigest()

def insert_user(username:str, email:str, password:str, db_info:str) -> bool:
    """
    Return True for success, False for failure.
    """
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(f"""INSERT INTO users (username, password, email, is_admin, is_premium, qr_count, qr_changes) 
                            VALUES ('{username}', '{hash_sha256(password)}', '{email}', False, False, 0, 0 );""")
            except ps2.errors.UniqueViolation:
                return False
    return True
