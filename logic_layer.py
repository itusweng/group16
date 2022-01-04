from typing import Optional, Tuple

from utils import hash_sha256, generate_qr, get_IP_location
from data_layer import User, get_user, insert_user, insert_qr_to_db, get_qr_by_user_id,\
    get_qr_by_qr_and_user_id, get_qr_by_id, update_qr_link, delete_qr_from_db, insert_qr_access, get_qr_history_from_db,\
    update_user_premium, get_all_users_db, delete_user, get_all_qr_db

with open("db_access_string.txt", "r") as f:
    db_info = f.read()

def login_user(username:str, password:str):
    """
    Authenticates with given username and password. Returns the user (if found, else None) and a success flag.
    """
    success = False
    user = get_user("username", username, db_info)
    hashed_password = hash_sha256(password)
    if user and hashed_password == user.hashed_password:
        success = True
    
    return user, success

def register_user(username:str, email:str, password:str):
    """ Returns a success flag """
    return insert_user(username, email, hash_sha256(password), db_info)

def decode_token(token: str): # Dummy function
    return get_user('id', token, db_info)

def insert_new_qr(link:str, user: User):
    """ Returns a success value. 0 is success, 1 is free user limitation 2 for error"""
    if not user.is_premium and user.qr_count>=3:
        return 1

    if insert_qr_to_db(link, user.id, db_info): return 0 # success
    return 2 # unexpected failure

def get_user_qr(user:User):
    """ Returns a list in JSON format of QR IDs and links """
    return [{'qr_id':qr[0], 'link':qr[1]} for qr in get_qr_by_user_id(user.id, db_info)]

def generate_qr_for_user(qr_id:str, user:User, version:str, size:str, embed_img_path:str, host:str):
    """ Generates and returns QR image if the owner is requesting, else returns None """
    if not get_qr_by_qr_and_user_id(qr_id, user.id, db_info):
        return None
    
    if version is None: version=5
    if size is None: size=1024
    return generate_qr(f"{host}/qr/{qr_id}", int(version), int(size), embed_img_path)

def get_qr_redirect_link(qr_id:str):
    """ Returns redirect link of a QR code"""
    return get_qr_by_id(qr_id, db_info)

def change_qr_link(qr_id:int, new_link:str, user:User):
    """ Changes the redirect link of a QR code. 0 for success, 1 for invalid ownership, 2 for error"""
    if not get_qr_by_qr_and_user_id(qr_id, user.id, db_info):
        return 1

    if update_qr_link(qr_id, new_link, user.id, db_info): return 0
    return 2

def delete_qr_code(qr_id:int, user:User):
    """ Deletes a QR code from DB. 0 for success, 1 for invalid ownership, 2 for error"""
    if not (get_qr_by_qr_and_user_id(qr_id, user.id, db_info) or user.is_admin):
        return 1

    if delete_qr_from_db(qr_id, user.id, db_info): return 0
    return 2

def log_qr_access(qr_id:str, agent:str, ip:str):
    country, city, lat, long = get_IP_location(ip)
    insert_qr_access(qr_id, ip, agent, country, city, lat, long, db_info)

def get_qr_access(qr_id:int, user:User):
    """ Returns QR access history. Returns 1 for invalid access"""
    if not (get_qr_by_qr_and_user_id(qr_id, user.id, db_info) or user.is_admin):
        return 1

    history = get_qr_history_from_db(qr_id, db_info)
    return [{'time':x[0], 'country':x[1], 'city':x[2], 'agent':x[3], 'latitude':x[4], 'longitude':x[5]} for x in history]

def set_user_premium(user:User):
    return update_user_premium(user.id, db_info)

def admin_get_all_users(user:User):
    if not user.is_admin:
        return 1
    
    return get_all_users_db(db_info)

def admin_ban_user(admin:User, user_id:str):
    if not admin.is_admin:
        return 1
    delete_user(user_id, db_info)
    return 0

def admin_get_all_qr(user:User):
    if not user.is_admin:
        return 1
    
    return get_all_qr_db(db_info)