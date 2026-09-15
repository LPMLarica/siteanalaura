from dados.database import SessionLocal
from dados.models import User


def get_or_create_user(data):
    """
    Busca um usuário local pelo ID do Supabase Auth (supabase_uid) ou
    pelo e-mail. Se não existir, cria um novo usuário local
    correlacionado à conta do Supabase.

    Espera receber um dicionário contendo:

        supabase_uid
        name
        email
    """

    if not data:
        raise ValueError(
            "Dados do usuário não foram fornecidos."
        )

    supabase_uid = data.get("supabase_uid")
    email = data.get("email")

    if not supabase_uid:
        raise ValueError(
            "ID do usuário (Supabase) não foi encontrado."
        )

    if not email:
        raise ValueError(
            "E-mail do usuário não foi encontrado."
        )

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.supabase_uid == supabase_uid
            )
            .first()
        )

        if user:
            user.name = data.get(
                "name",
                user.name
            )

            user.email = email

            db.commit()

            db.refresh(user)

            return user

        # Fallback: pode existir um usuário local antigo com o mesmo
        # e-mail (ex.: uma conta criada antes da migração para o
        # Supabase Auth) — correlaciona em vez de duplicar.
        user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if user:

            user.supabase_uid = supabase_uid

            user.name = data.get(
                "name",
                user.name
            )

            db.commit()

            db.refresh(user)

            return user

        user = User(
            supabase_uid=supabase_uid,
            name=data.get(
                "name",
                "Usuário"
            ),
            email=email,
            active=True
        )

        db.add(user)

        db.commit()

        db.refresh(user)

        return user

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()
