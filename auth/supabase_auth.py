"""
Autenticação de usuários via Supabase Auth (e-mail + senha).

Substitui o antigo fluxo de login com Google. O Supabase cuida de
armazenar as credenciais (com hash de senha, confirmação de e-mail,
etc.) — o app local só guarda uma cópia leve do usuário (nome, e-mail e
o "supabase_uid") na tabela `users` do nosso próprio banco, para
correlacionar pacientes/consultas/prontuários/pagamentos a quem os
criou (services/user_service.get_or_create_user).
"""

from supabase_client import get_supabase_client


def _user_from_supabase(user, fallback_name=None):

    metadata = getattr(user, "user_metadata", None) or {}

    name = (
        metadata.get("name")
        or fallback_name
        or (user.email.split("@")[0] if user.email else "Usuário")
    )

    return {
        "supabase_uid": user.id,
        "email": user.email,
        "name": name
    }


def sign_up(email, password, name):
    """
    Cria uma nova conta no Supabase Auth.

    Dependendo da configuração do projeto Supabase ("Confirm email"),
    a conta pode precisar de confirmação por e-mail antes do primeiro
    login funcionar — nesse caso o Supabase não retorna uma sessão
    aqui, e o próprio sign_in() abaixo vai falhar com uma mensagem
    clara ("Email not confirmed") até o usuário confirmar.
    """

    if not email or not password:
        raise ValueError("Informe e-mail e senha.")

    client = get_supabase_client()

    response = client.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {
                "name": name
            }
        }
    })

    if response.user is None:
        raise ValueError(
            "Não foi possível criar a conta. Verifique os dados e tente novamente."
        )

    return _user_from_supabase(response.user, fallback_name=name)


def sign_in(email, password):

    if not email or not password:
        raise ValueError("Informe e-mail e senha.")

    client = get_supabase_client()

    response = client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if response.user is None:
        raise ValueError("E-mail ou senha inválidos.")

    return _user_from_supabase(response.user)


def sign_out():

    try:
        client = get_supabase_client()
        client.auth.sign_out()
    except Exception:
        # Encerrar a sessão local (auth/session.py) já é suficiente do
        # ponto de vista do app; uma falha ao avisar o Supabase não deve
        # impedir o logout.
        pass
