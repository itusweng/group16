from typing import Optional
import hashlib
from PIL import Image
import qrcode
from datetime import datetime
import random
# import requests
# import json
            
def hash_sha256(string:str) -> str:
    m = hashlib.sha256(string.encode())
    return m.hexdigest()

def generate_qr(text:str, version:int=5, size:int=1024, embed_img_path:str=None) -> Image:
    """
    Returns a square PIL Image as the size given. 
    Version determines the complexity, and a image can be embedded to middle of the QR.
    """
    box_size = size // (17 + version*4 +4) # +4 is the border pixels. Change these to change the version.
    
    qr = qrcode.QRCode(version=version, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=box_size, border=2)
    qr.add_data(text)
    img = Image.new('RGB', (size,size), (255,255,255))
    qr_img = qr.make_image()
    # check if generated qr is larger than user input
    if qr_img.size[0] > img.size[0]:
        qr_img = qr_img.resize((size,size))
        offset = 0
    else: offset = (size % (17 + version*4 +4))//2 # find coordinates to paste
    
    img.paste(qr_img, (offset, offset))
    if embed_img_path is not None:
        with Image.open(embed_img_path) as embed_img:
            embed_img = embed_img.resize((int(size*0.2), (int(size*0.2))))
            img.paste(embed_img, ( int(size*0.4), int(size*0.4) ))
    
    return img

def timestamp():
    return  datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_IP_location(ip:str):
    # Dummy function during Offline testing (comments are the real function)
    """ Returns (Country, City, Latitude, Longitude) based on IP. On error returns None """
    locations = [('Turkey', 'Istanbul'), ('Turkey', 'Ankara'), ('Turkey', 'Izmir'), ('Germany', 'Berlin'), ('Germany', 'Munich'),\
    ('U.S.A', 'California'), ('U.S.A', 'Los Angeles'),]
    longitude = (random.random() - 0.5) * 180
    latitude = (random.random() - 0.5) * 90
    country, city = random.choice(locations)
    return country, city, latitude, longitude
    # API_ADDRESS = "https://geolocation-db.com/jsonp/"
    # try:
    #     ip_info = json.loads(requests.get(API_ADDRESS + ip).content.decode()[9:-1])
    #     return ip_info['country_name'], ip_info['city'], ip_info['latitude'], ip_info['longitude']
    # except:
    #     return None
