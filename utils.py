import psycopg2 as ps2
from pydantic import BaseModel
from typing import Optional
import hashlib
from PIL import Image
import qrcode

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

def generate_qr(text:str, size:int) -> Image:
    """
    Returns a square PIL Image as the size given. Uses QR Version 5 to encode 64 chars at most.
    """
    assert len(text)<=64 # 64 is the most alphanumeric chars allowed in Version 5
    box_size = size // (37+4) # 37 is Version 5 size. 4 is the border size. Change these to change the version.
    qr = qrcode.QRCode(version=5, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=box_size, border=2)
    qr.add_data(text)
    img = Image.new('RGB', (size,size), (255,255,255))
    offset = (img.size[0] - (box_size*41))//2 # calculate where to paste into middle
    img.paste(qr.make_image(), (offset, offset))
    return img
    
