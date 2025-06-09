from cryptography.fernet import Fernet
from config import KEY_FILE
import os

if os.path.exists(KEY_FILE):
    with open(KEY_FILE, 'rb') as f:
        key = f.read()
else:
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as f:
        f.write(key)

cipher = Fernet(key)

def encrypt(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt(token):
    return cipher.decrypt(token.encode()).decode()
