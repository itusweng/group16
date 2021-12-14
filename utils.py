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
