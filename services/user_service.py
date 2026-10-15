from sqlalchemy import select

from dados.database import session_scope
from dados.models import User


def _as_dict(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "professional_register": user.professional_register,
        "phone": user.phone,
        "default_session_minutes": user.default_session_minutes,
        "default_session_value": user.default_session_value,
        "active": user.active,
    }


def get_or_create_user(data):
    """
    Busca o usuário local pelo ID do Supabase Auth (ou pelo e-mail, para
    correlacionar contas antigas) e cria se ainda não existir.
    """

    supabase_uid = (data or {}).get("supabase_uid")
    email = ((data or {}).get("email") or "").lower()

    if not supabase_uid or not email:
        raise ValueError("Dados do usuário incompletos.")

    with session_scope() as db:
        user = db.scalar(select(User).where(User.supabase_uid == supabase_uid))

        if user is None:
            user = db.scalar(select(User).where(User.email == email))

            if user is not None:
                user.supabase_uid = supabase_uid

        if user is None:
            user = User(
                supabase_uid=supabase_uid,
                email=email,
                name=data.get("name") or email.split("@")[0],
                active=True,
            )
            db.add(user)
        else:
            user.email = email

            if not user.name and data.get("name"):
                user.name = data["name"]

        db.flush()

        return _as_dict(user)


def get_user(user_id):
    with session_scope() as db:
        user = db.get(User, user_id)
        return _as_dict(user) if user else None


def update_profile(user_id, **fields):
    allowed = {
        "name",
        "professional_register",
        "phone",
        "default_session_minutes",
        "default_session_value",
    }

    with session_scope() as db:
        user = db.get(User, user_id)

        if user is None:
            return None

        for key, value in fields.items():
            if key in allowed:
                setattr(user, key, value)

        db.flush()

        return _as_dict(user)
