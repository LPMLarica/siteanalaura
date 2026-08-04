import os
from cryptography.fernet import Fernet

KEY = os.getenv(
    "SECRET_KEY_CLINICAL"
)

if KEY:
    cipher = Fernet(
        KEY.encode()
    )

else:
    cipher = None


def encrypt_text(text):

    if not text:

        return None

    if not cipher:

        return text

    encrypted = cipher.encrypt(
        text.encode()
    )

    return encrypted.decode()


def decrypt_text(text):

    if not text:
        return None

    if not cipher:
        return text

    decrypted = cipher.decrypt(
        text.encode()
    )


    return decrypted.decode()