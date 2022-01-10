from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Form, BackgroundTasks, Request, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from logic_layer import login_user, register_user, decode_token, insert_new_qr, get_user_qr, \
    generate_qr_for_user, get_qr_redirect_link, change_qr_link, delete_qr_code, log_qr_access, get_qr_access,\
    set_user_premium, admin_get_all_users, admin_ban_user, admin_get_all_qr

SERVER_HOST = "http://127.0.0.1:8000"
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

# LOGIN / REGISTER ###############################################################
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """ Used to get the access token that must be supplied in the headers of other GET/POST methods."""
    user, success = login_user(form_data.username, form_data.password)
    if not success:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    print(dict(user))
    return {"access_token": user.id, "token_type": "bearer"}

@app.post("/register", status_code=200)
async def login(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    """ Registers the user to database if username and email are unique. """
    success = register_user(username, email, password)
    if not success:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

# QR CODE ###############################################################
@app.post("/create_qr")
async def create_qr(link: str = Form(...), token: str = Depends(oauth2_scheme)):
    """ Adds the QR to the database. This method does not return an image. """
    user = decode_token(token)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found.")
    status = insert_new_qr(link, user)
    if status==1:
        raise HTTPException(status_code=400, detail="Free users can generate up to 3 QR codes. Upgrade to premium or delete a QR code to generate a new one.")
    if status==2:
        raise HTTPException(status_code=400, detail="Unexpected error, contact an administrator.")

@app.get("/my_qr_codes")
async def my_qr_codes(token:str = Depends(oauth2_scheme)):
    """ Returns the QR code data in JSON format. This method does not return an image."""
    user = decode_token(token)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found.")
    return get_user_qr(user)

@app.post("/get_qr_img")
async def get_qr_img(qr_id:str, bg_task:BackgroundTasks, file: Optional[UploadFile] = File(None), version:str=None, size:str=None,  token:str = Depends(oauth2_scheme)):
    """ Creates and returns an image based on user selected values. """
    user = decode_token(token)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found.")
    if file is not None:
        contents = await file.read()
        filename = file.filename
        with open(filename, "wb+") as file_object:
            file_object.write(contents)
        bg_task.add_task(os.remove, filename)
    else: filename = None
    requested_qr = generate_qr_for_user(qr_id, user, version, size, filename, SERVER_HOST)
    if requested_qr is None:
        raise HTTPException(status_code=400, detail="Only the owners can see their QR codes.")
    fname = f"{qr_id}.png"
    requested_qr.save(fname)
    bg_task.add_task(os.remove, fname)
    return FileResponse(fname, background=bg_task)

@app.get("/qr/{qr_id}", status_code=200)# Get redirect link from qr
async def redirect_from_qr(qr_id:str, request:Request):
    """ This method redirects when a QR is scanned to its respective URL."""
    # Get Information about the Request:
    agent = request.headers.get('user-agent')
    ip = request.client.host
    log_qr_access(qr_id, agent, ip)
    # Redirect
    redirect_link = get_qr_redirect_link(qr_id)
    if redirect_link is None:
        raise HTTPException(status_code=400, detail="Invalid QR code.")
    
    return JSONResponse(status_code=302, headers={"Location":redirect_link})

@app.post("/update_qr")
async def update_qr(qr_id:int, new_link:str, token:str = Depends(oauth2_scheme)):
    """ Updates the redirect link of a QR if the sender has ownership. """
    user = decode_token(token)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found.")
    status = change_qr_link(qr_id, new_link, user)
    if status==1:
        raise HTTPException(status_code=400, detail="Only the owners can edit their QR codes.")
    if status==2:
        raise HTTPException(status_code=400, detail="Unexpected error, contact an administrator.")

@app.post("/delete_qr")
async def delete_qr(qr_id:int, token:str = Depends(oauth2_scheme)):
    """ Deletes QR from database if the sender has ownership. """
    user = decode_token(token)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found.")
    status = delete_qr_code(qr_id, user)
    if status==1:
        raise HTTPException(status_code=400, detail="Only the owners can delete their QR codes.")
    if status==2:
        raise HTTPException(status_code=400, detail="Unexpected error, contact an administrator.")

@app.get("/get_qr_stats")
async def get_qr_stats(qr_id:int, token:str = Depends(oauth2_scheme)):
    """ Returns the access history of a QR code in JSON format if the sender has ownership."""
    user = decode_token(token)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found.")
    access_history = get_qr_access(qr_id, user)
    if access_history==1:
        raise HTTPException(status_code=400, detail="Only the owners can view access history of their QR codes.")
    return access_history

# PREMIUM / ADMIN ####################################################################

@app.get("/set_premium")
async def set_premium(token:str = Depends(oauth2_scheme)):
    """ Sets the account status of the sender to premium"""
    user = decode_token(token)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found.")
    status = set_user_premium(user)
    if status==False:
        raise HTTPException(status_code=400, detail="Unexpected error, contact an administrator.")

@app.get("/all_users")
async def get_all_users(token:str = Depends(oauth2_scheme)):
    """ Allows the admin to get the data for all users. """
    admin = decode_token(token)
    results = admin_get_all_users(admin)
    if results==1:
        raise HTTPException(status_code=400, detail="Only the admins can view all users.")
    return results

@app.post("/ban_user")
async def ban_user(user_id:str, token:str = Depends(oauth2_scheme)):
    """ Allows the admin to ban a user, deleting all QR codes etc. from the database. """
    admin = decode_token(token)
    results = admin_ban_user(admin, user_id)
    if results==1:
        raise HTTPException(status_code=400, detail="Only the admins can ban users.")

@app.get("/all_qr_codes")
async def get_all_qr(token:str = Depends(oauth2_scheme)):
    """ Allows the admin to get the data for all QR codes. """
    admin = decode_token(token)
    results = admin_get_all_qr(admin)
    if results==1:
        raise HTTPException(status_code=400, detail="Only the admins can view all QR codes.")
    return results