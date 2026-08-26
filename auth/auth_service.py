from google.oauth2 import id_token
from google.auth.transport import requests


def decode_google_user(credentials):
    """
    Valida o ID Token recebido do Google
    e transforma os dados em um formato
    utilizado pelo sistema.
    """

    if credentials is None:
        raise ValueError(
            "Credenciais Google não foram fornecidas."
        )

    if not getattr(credentials, "id_token", None):
        raise ValueError(
            "ID Token do Google não foi encontrado."
        )

    token_info = id_token.verify_oauth2_token(
        credentials.id_token,
        requests.Request()
    )

    google_id = token_info.get("sub")
    email = token_info.get("email")

    if not google_id:
        raise ValueError(
            "Google ID não encontrado no token."
        )

    if not email:
        raise ValueError(
            "E-mail não encontrado no token Google."
        )

    return {
        "google_id": google_id,

        "name": token_info.get(
            "name",
            "Usuário"
        ),

        "email": email,

        "picture": token_info.get(
            "picture"
        )
    }