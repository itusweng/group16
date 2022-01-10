from datetime import datetime
from PIL import Image
from utils import hash_sha256, generate_qr, timestamp, get_IP_location
from data_layer import User
from logic_layer import login_user, register_user, decode_token, insert_new_qr, get_user_qr, generate_qr_for_user, get_qr_redirect_link, change_qr_link, delete_qr_code,log_qr_access,  get_qr_access, set_user_premium, admin_get_all_users, admin_ban_user, admin_get_all_qr

# UTILISATIONS UNIT TESTS

def test_hash_sha256():
    assert hash_sha256('testing') == 'cf80cd8aed482d5d1527d7dc72fceff84e6326592848447d2dc0b0e87dfc9a90'

def test_generate_qr():
    img = generate_qr('https://www.itu.edu.tr/')
    histogram = img.histogram()
    assert histogram == [391680, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 656896, 391680, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 656896, 391680, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 656896]

def test_2_generate_qr():
    img = generate_qr('https://www.itu.edu.tr/', 5, 124, 'itu_logo.jpg')
    histogram = img.histogram()
    assert histogram == [5796, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 2, 4, 0, 2, 4, 5, 2, 2, 1, 5, 4, 2, 2, 1, 2, 1, 2, 3, 7, 2, 4, 2, 5, 2, 1, 2, 1, 2, 3, 2, 1, 2, 2, 0, 4, 4, 2, 0, 3, 2, 2, 1, 3, 5, 3, 0, 7, 4, 1, 5, 1, 3, 3, 5, 7, 0, 1, 8, 5, 5, 7, 5, 9399, 5796, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 2, 4, 1, 3, 3, 5, 2, 2, 4, 3, 2, 3, 2, 0, 2, 3, 2, 2, 8, 3, 4, 5, 2, 2, 3, 2, 3, 4, 6, 5, 1, 4, 4, 2, 5, 4, 2, 1, 4, 1, 2, 2, 0, 1, 2, 2, 1, 1, 1, 1, 6, 0, 4, 8, 1, 4, 5, 7, 2, 4, 6, 9397, 5796, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 3, 2, 1, 0, 1, 2, 1, 0, 0, 1, 0, 0, 3, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 5, 6, 4, 8, 2, 6, 6, 1, 1, 7, 3, 10, 7, 4, 1, 4, 3, 5, 2, 2, 11, 6, 2, 2, 0, 5, 2, 3, 2, 1, 2, 6, 4, 7, 7, 6, 9399]

def test_timestamp():
    assert timestamp() == datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def test_get_IP_location():
    assert get_IP_location('85.99.20.13') != ('Turkey', 'Istanbul', '0', '0')

# LOGIC LAYER UNIT TESTS

def test_login_user(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_user', return_value=user)
    assert login_user('username', 'password') == (User(id='123',username='username',hashed_password='hashed_password'),False)

def test_2_login_user(mocker):
    user = User(id='123',username='username',hashed_password='5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8')
    mocker.patch('logic_layer.get_user', return_value=user)
    assert login_user('username', 'password') == (User(id='123',username='username',hashed_password='5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),True)

def test_register_user(mocker):
    mocker.patch('logic_layer.insert_user', return_value=True)
    assert register_user('username', 'email', 'password') == True
    
def test_decode_token(mocker):
    mocker.patch('logic_layer.get_user', return_value=True)
    assert decode_token('token') == True

def test_insert_new_qr():
    user = User(id='123',username='username',hashed_password='hashed_password',qr_count=3)
    assert insert_new_qr('link',user) == 1

def test_2_insert_new_qr(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password',qr_count=0)
    mocker.patch('logic_layer.insert_qr_to_db', return_value=True)
    assert insert_new_qr('link',user) == 0

def test_3_insert_new_qr(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password',qr_count=0)
    mocker.patch('logic_layer.insert_qr_to_db', return_value=False)
    assert insert_new_qr('link',user) == 2

def test_generate_qr_for_user(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_qr_by_qr_and_user_id', return_value=False)
    assert generate_qr_for_user('qr_id', user, 'version', 'size', 'embed_img_path', 'host') == None

def test_2_generate_qr_for_user(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_qr_by_qr_and_user_id', return_value=True)
    mocker.patch('logic_layer.generate_qr', return_value=True)
    assert generate_qr_for_user('qr_id', user, None, None, 'embed_img_path', 'host') == True

def test_get_qr_redirect_link(mocker):
    mocker.patch('logic_layer.get_qr_by_id', return_value=None)
    assert get_qr_redirect_link('qr_id') == None

def test_2_get_qr_redirect_link(mocker):
    link = ['https://www.itu.edu.tr/', 0]
    mocker.patch('logic_layer.get_qr_by_id', return_value=link)
    assert get_qr_redirect_link('qr_id') == 'https://www.itu.edu.tr/'

def test_3_get_qr_redirect_link(mocker):
    link = ['www.itu.edu.tr/', 0]
    mocker.patch('logic_layer.get_qr_by_id', return_value=link)
    assert get_qr_redirect_link('qr_id') == 'https://www.itu.edu.tr/'

def test_change_qr_link(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_qr_by_qr_and_user_id', return_value=False)
    assert change_qr_link(123,'new_link',user) == 1

def test_2_change_qr_link(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_qr_by_qr_and_user_id', return_value=True)
    mocker.patch('logic_layer.update_qr_link', return_value=True)
    assert change_qr_link(123,'new_link',user) == 0

def test_3_change_qr_link(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_qr_by_qr_and_user_id', return_value=True)
    mocker.patch('logic_layer.update_qr_link', return_value=False)
    assert change_qr_link(123,'new_link',user) == 2

def test_delete_qr_code(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_qr_by_qr_and_user_id', return_value=False)
    assert delete_qr_code(123,user) == 1

def test_2_delete_qr_code(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_qr_by_qr_and_user_id', return_value=True)
    mocker.patch('logic_layer.delete_qr_from_db', return_value=True)
    assert delete_qr_code(123,user) == 0

def test_3_delete_qr_code(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_qr_by_qr_and_user_id', return_value=True)
    mocker.patch('logic_layer.delete_qr_from_db', return_value=False)
    assert delete_qr_code(123,user) == 2

def test_log_qr_access(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_IP_location', return_value=('Turkey','Istanbul','0','0'))
    mocker.patch('logic_layer.insert_qr_access', return_value=False)
    assert log_qr_access('qr_id','agent','123') == None

def test_get_qr_access(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.get_qr_by_qr_and_user_id', return_value=False)
    assert get_qr_access(123,user) == 1

def test_set_user_premium(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password')
    mocker.patch('logic_layer.update_user_premium', return_value=True)
    assert set_user_premium(user) == True

def test_admin_get_all_users():
    user = User(id='123',username='username',hashed_password='hashed_password')
    assert admin_get_all_users(user) == 1

def test_2_admin_get_all_users(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password',is_admin=True)
    mocker.patch('logic_layer.get_all_users_db', return_value=True)
    assert admin_get_all_users(user) == True

def test_admin_ban_user():
    user = User(id='123',username='username',hashed_password='hashed_password')
    assert admin_ban_user(user,'123') == 1

def test_2_admin_ban_user(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password',is_admin = True)
    mocker.patch('logic_layer.delete_user', return_value=True)
    assert admin_ban_user(user,'123') == 0

def test_admin_get_all_qr():
    user = User(id='123',username='username',hashed_password='hashed_password')
    assert admin_get_all_qr(user) == 1

def test_2_admin_get_all_qr(mocker):
    user = User(id='123',username='username',hashed_password='hashed_password',is_admin = True)
    mocker.patch('logic_layer.get_all_qr_db', return_value=True)
    assert admin_get_all_qr(user) == True
