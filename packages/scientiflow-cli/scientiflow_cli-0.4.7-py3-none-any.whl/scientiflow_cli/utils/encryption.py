import os
from getpass import getpass
from base64 import b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_fernet_key(password: str, salt: str) -> bytes:
    salt = urlsafe_b64decode(salt)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # Desired key length
        salt=salt,
        iterations=100000  # Increase iterations for stronger security
    )
    key = kdf.derive(password.encode())
    key = b64encode(key)
    return key


def decrypt_fernet(encrypted_text: str, salt: str) -> str:
    password = getpass("> Enter password: ")
    key = derive_fernet_key(password, salt)
    fernet = Fernet(key)
    decrypted_text = fernet.decrypt(encrypted_text.encode())
    return decrypted_text.decode()


def encrypt_fernet(password: str, salt: str, text: str) -> str:
    key = derive_fernet_key(password, salt)
    fernet = Fernet(key)
    encrypted_text = fernet.encrypt(text.encode())
    
    return encrypted_text.decode()

