"""
Criptografia simétrica (Fernet) do conteúdo dos prontuários.

A chave vem de ``SECRET_KEY`` (secrets do Streamlit ou .env). Ela NÃO
pode ser trocada depois que houver prontuários gravados — os registros
antigos deixariam de ser legíveis. Guarde uma cópia segura dela.

Gerar uma chave nova:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from config.settings import settings


@lru_cache(maxsize=1)
def _cipher():
    key = settings.SECRET_KEY

    if not key:
        raise RuntimeError(
            "SECRET_KEY não está definida — os prontuários precisam ser "
            "criptografados antes de serem gravados."
        )

    try:
        return Fernet(key.encode())
    except (ValueError, TypeError) as exc:
        raise RuntimeError("SECRET_KEY não é uma chave Fernet válida.") from exc


def encrypt_text(text):
    if not text:
        return None

    return _cipher().encrypt(text.encode("utf-8")).decode("ascii")


def decrypt_text(token):
    if not token:
        return ""

    try:
        return _cipher().decrypt(token.encode("ascii")).decode("utf-8")
    except InvalidToken:
        return "[não foi possível descriptografar este registro — verifique a SECRET_KEY]"
