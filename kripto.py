# kripto.py
import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken

def get_key_from_password(password: str, salt: bytes) -> bytes:
    """Menurunkan kunci enkripsi dari password menggunakan PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    # Fernet membutuhkan kunci yang di-encode dengan base64
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt(data: bytes, password: str) -> bytes:
    """Mengenkripsi data menggunakan password."""
    # 1. Buat salt acak untuk setiap enkripsi
    salt = os.urandom(16)
    
    # 2. Turunkan kunci dari password dan salt
    key = get_key_from_password(password, salt)
    
    # 3. Enkripsi data
    f = Fernet(key)
    encrypted_data = f.encrypt(data)
    
    # 4. Gabungkan salt dengan data terenkripsi agar bisa digunakan saat dekripsi
    return salt + encrypted_data

def decrypt(token: bytes, password: str) -> bytes:
    """Mendekripsi token menggunakan password."""
    try:
        # 1. Pisahkan salt dan data terenkripsi dari token
        salt = token[:16]
        encrypted_data = token[16:]
        
        # 2. Turunkan kunci dari password dan salt yang sama
        key = get_key_from_password(password, salt)
        
        # 3. Dekripsi data
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data
    except InvalidToken:
        # Ini terjadi jika password salah atau data korup
        print("ERROR: Password salah atau token dekripsi tidak valid.")
        return None
    except Exception as e:
        print(f"Terjadi error saat dekripsi: {e}")
        return None