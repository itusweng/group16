from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Form, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, JSONResponse
import os

from logic_layer import login_user, register_user, decode_token, insert_new_qr, get_user_qr, \
    generate_qr_for_user, get_qr_redirect_link, change_qr_link, delete_qr_code


SERVER_HOST = "http://127.0.0.1:8000"
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# LOGIN / REGISTER ###############################################################
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user, success = login_user(form_data.username, form_data.password)
    if not success:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    print(dict(user))
    return {"access_token": user.id, "token_type": "bearer"}

@app.post("/register", status_code=200)
async def login(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    success = register_user(username, email, password)
    if not success:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

# QR CODE ###############################################################
@app.post("/create_qr")
async def create_qr(link: str = Form(...), token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    status = insert_new_qr(link, user)
    if status==1:
        raise HTTPException(status_code=400, detail="Free users can generate up to 3 QR codes. Upgrade to premium or delete a QR code to generate a new one.")
    if status==2:
        raise HTTPException(status_code=400, detail="Unexpected error, contact an administrator.")

@app.get("/my_qr_codes")
async def my_qr_codes(token:str = Depends(oauth2_scheme)):
    user = decode_token(token)
    return get_user_qr(user)

@app.post("/get_qr_img")
async def get_qr_img(qr_index:str, bg_task:BackgroundTasks, token:str = Depends(oauth2_scheme)):
    user = decode_token(token)
    requested_qr = generate_qr_for_user(qr_index, user, SERVER_HOST)
    if requested_qr is None:
        raise HTTPException(status_code=400, detail="Only the owners can see their QR codes.")
    fname = f"{qr_index}.png"
    requested_qr.save(fname)
    bg_task.add_task(os.remove, fname)
    return FileResponse(fname, background=bg_task)

@app.get("/qr/{qr_id}", status_code=200)# Get redirect link from qr
async def redirect_from_qr(qr_id:str):
    redirect_link = get_qr_redirect_link(qr_id)
    if redirect_link is None:
        raise HTTPException(status_code=400, detail="Invalid QR code.")
    
    return {"redirect_to":redirect_link[0]}
    #return JSONResponse(status_code=302, headers={"Location":redirect_link}) TODO

@app.post("/update_qr")
async def update_qr(qr_index:int, new_link:str, token:str = Depends(oauth2_scheme)):
    user = decode_token(token)
    status = change_qr_link(qr_index, new_link, user)
    if status==1:
        raise HTTPException(status_code=400, detail="Only the owners can edit their QR codes.")
    if status==2:
        raise HTTPException(status_code=400, detail="Unexpected error, contact an administrator.")

@app.post("/delete_qr")
async def delete_qr(qr_index:int, token:str = Depends(oauth2_scheme)):
    user = decode_token(token)
    status = delete_qr_code(qr_index, user)
    if status==1:
        raise HTTPException(status_code=400, detail="Only the owners can delete their QR codes.")
    if status==2:
        raise HTTPException(status_code=400, detail="Unexpected error, contact an administrator.")

