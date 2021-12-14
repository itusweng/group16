from typing import Optional
import hashlib
from PIL import Image
import qrcode
from datetime import datetime
            
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
    
