from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Form, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from pydantic import BaseModel
import psycopg2 as ps2
import os

from utils import User, get_user, hash_sha256, insert_user, generate_qr

with open("db_access_string.txt", "r") as f:
    db_info = f.read()
SERVER_HOST = "http://127.0.0.1:8000"
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# LOGIN / REGISTER ###############################################################
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user("username", form_data.username, db_info)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    hashed_password = hash_sha256(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.id, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(user_id: str = Depends(oauth2_scheme)):
    return user_id

@app.post("/register", status_code=200)
async def login(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    success = insert_user(username, email, password, db_info)
    if not success:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

# QR CODE ###############################################################
@app.post("/create_qr")
async def create_qr(link: str = Form(...), user_id: str = Depends(oauth2_scheme)):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM users WHERE id={user_id} AND (is_premium IS TRUE OR qr_count<3);")
            cur_return = cur.fetchone()
            if not cur_return:
                raise HTTPException(status_code=400, detail="Free users can generate up to 3 QR codes. Upgrade to premium or delete a QR code to generate a new one.")
            cur.execute(f"INSERT INTO qr_codes (user_id, outgoing_link) VALUES ({user_id}, '{link}');")
            cur.execute(f"UPDATE users SET qr_count = qr_count + 1 WHERE id={user_id};")

@app.get("/my_qr_codes")
async def get_all_qr(user_id: str = Depends(oauth2_scheme)):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM qr_codes WHERE user_id={user_id} ORDER BY id ASC;")
            cur_return = cur.fetchall()
            return [{'i':i, 'link':qr[2]} for i, qr in enumerate(cur_return)]

@app.post("/get_qr_img")
async def get_qr_img(qr_index:int, bg_task:BackgroundTasks, user_id: str = Depends(oauth2_scheme)):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM qr_codes WHERE user_id={user_id} ORDER BY id ASC;")
            try:
                requested_qr = cur.fetchall()[qr_index]
            except IndexError:
                raise HTTPException(status_code=400, detail="Invalid QR index.")
    fname = f"{requested_qr[0]}.png"
    generate_qr(SERVER_HOST + f"/qr/{requested_qr[0]}", 1024).save(fname)
    bg_task.add_task(os.remove, fname)
    return FileResponse(fname, background=bg_task)

@app.get("/qr/{qr_id}") # Get redirect link from qr
async def redirect_from_qr(qr_id:str):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT outgoing_link FROM qr_codes WHERE id={qr_id};")
            cur_return = cur.fetchone()
            if not cur_return:
                raise HTTPException(status_code=400, detail="Invalid QR code.")
            return {"redirect_link":cur_return[0]}

@app.post("/update_qr")
async def update_qr(qr_index:int, new_link:str, user_id: str = Depends(oauth2_scheme)):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM qr_codes WHERE user_id={user_id} ORDER BY id ASC;")
            try:
                requested_qr = cur.fetchall()[qr_index]
            except IndexError:
                raise HTTPException(status_code=400, detail="Invalid QR index.")
            
            cur.execute(f"UPDATE qr_codes SET outgoing_link='{new_link}' WHERE id={requested_qr[0]};")
            if cur.rowcount==0:
                raise HTTPException(status_code=400, detail="Invalid QR index.")

@app.post("/delete_qr")
async def delete_qr(qr_index:int, user_id: str = Depends(oauth2_scheme)):
    with ps2.connect(db_info) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM qr_codes WHERE user_id={user_id} ORDER BY id ASC;")
            try:
                requested_qr = cur.fetchall()[qr_index]
            except IndexError:
                raise HTTPException(status_code=400, detail="Invalid QR index.")
            
            cur.execute(f"DELETE FROM qr_codes WHERE id={requested_qr[0]};")
            if cur.rowcount==0:
                raise HTTPException(status_code=400, detail="Invalid QR index.")

