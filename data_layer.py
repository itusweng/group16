import psycopg2 as ps2
from typing import Optional
from pydantic import BaseModel
from utils import timestamp

class User(BaseModel):
    id: str
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
    conn.close()
    if not cur_return: # No user found
        return None
    return User(**dict(zip(['id', 'username', 'hashed_password', 'email', 'is_admin', 'is_premium', 'qr_count', 'qr_changes'], cur_return)))

def insert_user(username:str, email:str, password:str, db_info:str) -> bool:
    """
    Return True for success, False for Unique violation.
    """
    status = True
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(f"""INSERT INTO users (username, password, email, is_admin, is_premium, qr_count, qr_changes) 
                            VALUES ('{username}', '{password}', '{email}', False, False, 0, 0 );""")
            except ps2.errors.UniqueViolation:
                status = False
    conn.close()
    return status

def insert_qr_to_db(link:str, user_id:str, db_info:str):
    """
    Return True for success, False for failure.
    """
    status = True
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(f"INSERT INTO qr_codes (user_id, outgoing_link) VALUES ({user_id}, '{link}');")
                cur.execute(f"UPDATE users SET qr_count = qr_count + 1 WHERE id={user_id};")
            except:
                status = False
    conn.close()
    return status

def get_qr_by_user_id(user_id:str, db_info:str):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, outgoing_link FROM qr_codes WHERE user_id={user_id} ORDER BY id ASC;")
            cur_return = cur.fetchall()
    conn.close()
    return cur_return

def get_qr_by_qr_and_user_id(qr_id:str, user_id:str, db_info:str):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM qr_codes WHERE id={qr_id} AND user_id={user_id};")
            cur_return = cur.fetchone()
    conn.close()
    return cur_return

def get_qr_by_id(qr_id:str, db_info:str):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT outgoing_link FROM qr_codes WHERE id={qr_id};")
            cur_return = cur.fetchone()
    conn.close()
    return cur_return

def update_qr_link(qr_id:str, new_link:str, user_id:str, db_info:str):
    try:
        with ps2.connect(db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT outgoing_link FROM qr_codes WHERE id={qr_id};")
                old_link = cur.fetchone()[0]
                cur.execute(f"UPDATE qr_codes SET outgoing_link='{new_link}' WHERE id={qr_id};")
                cur.execute(f"UPDATE users SET qr_changes = qr_changes + 1 WHERE id={user_id};")
                cur.execute(f"INSERT INTO qr_change_history (qr_id, change_time, from_link, to_link) VALUES ({qr_id},'{timestamp()}','{old_link}','{new_link}');")
    except:
        conn.close()
        return False

    conn.close()
    return True


def delete_qr_from_db(qr_id:str, user_id:str, db_info:str):
    try:
        with ps2.connect(db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM qr_codes WHERE id={qr_id};")
                cur.execute(f"UPDATE users SET qr_count = qr_count - 1 WHERE id={user_id};")
    except:
        conn.close()
        return False

    conn.close()
    return True

def insert_qr_access(qr_id:str, ip:str, agent:str, country:str, city:str, lat:str, long:str, db_info:str):
    try:
        with ps2.connect(db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(f"""INSERT INTO qr_access_history VALUES ({qr_id}, '{timestamp()}', '{ip}', '{country}', '{city}', '{agent}', {lat}, {long});""")
    except:
        pass

    conn.close()

def get_qr_history_from_db(qr_id:str, db_info:str):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT access_time, country, city, agent, latitude, longitude FROM qr_access_history WHERE qr_id={qr_id};")
            cur_return = cur.fetchall()
    conn.close()
    return cur_return

def update_user_premium(user_id:str, db_info:str):
    try:
        with ps2.connect(db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(f"UPDATE users SET is_premium=TRUE WHERE id={user_id};")
        conn.close()
    except: return False # error occured
    return True # no errors

def get_all_users_db(db_info:str):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM users;")
            cur_return = cur.fetchall()
    conn.close()
    return cur_return

def delete_user(user_id:str, db_info:str):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM users WHERE id={user_id};")
    conn.close()

def get_all_qr_db(db_info:str):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM qr_codes;")
            cur_return = cur.fetchall()
    conn.close()
    return cur_return