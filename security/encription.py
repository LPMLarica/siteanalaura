import os
from cryptography.fernet import Fernet, InvalidToken

KEY = os.getenv(
    "SECRET_KEY"
)

if not KEY:
    raise RuntimeError(
        "SECRET_KEY não está definida. Os prontuários precisam ficar "
        "criptografados no banco, então o app se recusa a iniciar sem "
        "uma chave Fernet válida em vez de gravar dados clínicos em "
        "texto puro. Gere uma com: python -c \"from cryptography.fernet "
        "import Fernet; print(Fernet.generate_key().decode())\" e "
        "coloque o resultado na variável SECRET_KEY do seu .env."
    )

try:
    cipher = Fernet(
        KEY.encode()
    )
except (ValueError, TypeError) as exc:
    raise RuntimeError(
        "SECRET_KEY está definida, mas não é uma chave Fernet válida. "
        "Gere uma com: python -c \"from cryptography.fernet import "
        "Fernet; print(Fernet.generate_key().decode())\" e coloque o "
        "resultado na variável SECRET_KEY do seu .env."
    ) from exc


def encrypt_text(text):

    if not text:

        return None

    encrypted = cipher.encrypt(
        text.encode()
    )

    return encrypted.decode()


def decrypt_text(text):

    if not text:
        return None

    try:
        decrypted = cipher.decrypt(
            text.encode()
        )
    except InvalidToken:
        # Dado gravado antes da criptografia estar ativa, ou com outra
        # chave. Mostra algo claro em vez de quebrar a tela inteira.
        return "[não foi possível descriptografar este registro]"

    return decrypted.decode()
