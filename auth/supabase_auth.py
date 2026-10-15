"""
Autenticação via Supabase Auth (e-mail + senha).

O Supabase guarda as credenciais (hash da senha, confirmação de e-mail,
recuperação de senha). O app mantém só uma cópia leve do usuário na
tabela ``users`` para relacionar pacientes, consultas etc.
"""

import logging

from auth.supabase_client import new_supabase_client
from config.settings import settings

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Erro de autenticação com mensagem pronta para a tela."""


_MESSAGES = {
    "invalid login credentials": "E-mail ou senha inválidos.",
    "email not confirmed": (
        "Seu e-mail ainda não foi confirmado. Abra o link enviado para a "
        "sua caixa de entrada e tente novamente."
    ),
    "user already registered": "Já existe uma conta com este e-mail.",
    "already been registered": "Já existe uma conta com este e-mail.",
    "rate limit": (
        "Muitas tentativas em pouco tempo. Aguarde alguns minutos e tente novamente."
    ),
    "for security purposes": (
        "Por segurança, aguarde alguns segundos antes de pedir outro e-mail."
    ),
    "token has expired or is invalid": "Código inválido ou expirado. Peça um novo código.",
    "password should be": "A senha precisa ter pelo menos 8 caracteres.",
    "weak password": "Senha fraca. Use pelo menos 8 caracteres, com letras e números.",
    "new password should be different": "A nova senha precisa ser diferente da atual.",
    "signups not allowed": "O cadastro de novas contas está desativado.",
    "unable to validate email": "E-mail inválido.",
}


def _translate(error, fallback):
    text = str(error or "").lower()

    for needle, message in _MESSAGES.items():
        if needle in text:
            return AuthError(message)

    logger.warning("Erro de autenticação não mapeado: %s", error)

    return AuthError(fallback)


def _user_dict(user, fallback_name=None):
    metadata = getattr(user, "user_metadata", None) or {}
    email = (user.email or "").lower()

    return {
        "supabase_uid": str(user.id),
        "email": email,
        "name": metadata.get("name") or fallback_name or email.split("@")[0],
    }


def _check_allowed(email):
    if not settings.email_allowed(email):
        raise AuthError("Este e-mail não tem permissão para acessar o sistema.")


def sign_in(email, password):
    email = (email or "").strip().lower()

    if not email or not password:
        raise AuthError("Informe e-mail e senha.")

    _check_allowed(email)

    try:
        response = new_supabase_client().auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as error:
        raise _translate(error, "Não foi possível entrar. Tente novamente.") from error

    if response.user is None:
        raise AuthError("E-mail ou senha inválidos.")

    return _user_dict(response.user)


def sign_up(email, password, name):
    """
    Cria a conta. Retorna (usuario, precisa_confirmar_email).
    """

    email = (email or "").strip().lower()

    if not settings.ALLOW_SIGNUP:
        raise AuthError("O cadastro de novas contas está desativado.")

    _check_allowed(email)

    try:
        response = new_supabase_client().auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {"data": {"name": name}},
            }
        )
    except Exception as error:
        raise _translate(error, "Não foi possível criar a conta.") from error

    if response.user is None:
        raise AuthError("Não foi possível criar a conta.")

    # Com "Confirm email" ligado, o Supabase não devolve sessão e também
    # não acusa e-mail repetido (devolve um usuário sem identidades).
    if response.session is None and not (response.user.identities or []):
        raise AuthError("Já existe uma conta com este e-mail.")

    return _user_dict(response.user, fallback_name=name), response.session is None


def send_password_reset(email):
    email = (email or "").strip().lower()

    if not email:
        raise AuthError("Informe o e-mail da conta.")

    try:
        new_supabase_client().auth.reset_password_for_email(email)
    except Exception as error:
        raise _translate(error, "Não foi possível enviar o e-mail.") from error


def reset_password_with_code(email, code, new_password):
    """Conclui a recuperação com o código de 6 dígitos recebido por e-mail."""

    email = (email or "").strip().lower()
    client = new_supabase_client()

    try:
        client.auth.verify_otp(
            {"email": email, "token": (code or "").strip(), "type": "recovery"}
        )
        client.auth.update_user({"password": new_password})
    except Exception as error:
        raise _translate(error, "Não foi possível redefinir a senha.") from error


def change_password(email, current_password, new_password):
    client = new_supabase_client()

    try:
        client.auth.sign_in_with_password(
            {"email": email, "password": current_password}
        )
    except Exception as error:
        raise AuthError("A senha atual está incorreta.") from error

    try:
        client.auth.update_user({"password": new_password})
    except Exception as error:
        raise _translate(error, "Não foi possível alterar a senha.") from error


def validate_new_password(password, confirmation):
    if not password or len(password) < 8:
        return "A senha precisa ter pelo menos 8 caracteres."

    if password.isdigit() or password.isalpha():
        return "Use letras e números na senha."

    if password != confirmation:
        return "As senhas não coincidem."

    return None
