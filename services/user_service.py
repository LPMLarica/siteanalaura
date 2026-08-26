from dados.database import SessionLocal
from dados.models import User


def get_or_create_user(data):
    """
    Busca um usuário pelo Google ID ou e-mail.
    Se não existir, cria um novo usuário.

    Espera receber um dicionário contendo:

        google_id
        name
        email
        picture
    """

    if not data:
        raise ValueError(
            "Dados do usuário Google não foram fornecidos."
        )

    google_id = data.get("google_id")
    email = data.get("email")

    if not google_id:
        raise ValueError(
            "Google ID não foi encontrado na autenticação."
        )

    if not email:
        raise ValueError(
            "E-mail do usuário Google não foi encontrado."
        )

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.google_id == google_id
            )
            .first()
        )

        if user:
            user.name = data.get(
                "name",
                user.name
            )

            user.picture = data.get(
                "picture",
                user.picture
            )

            user.email = email

            db.commit()

            db.refresh(user)

            return user

        # Fallback:
        # pode existir um usuário antigo com o mesmo e-mail
        user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if user:

            user.google_id = google_id

            user.name = data.get(
                "name",
                user.name
            )

            user.picture = data.get(
                "picture",
                user.picture
            )

            db.commit()

            db.refresh(user)

            return user

        user = User(
            google_id=google_id,
            name=data.get(
                "name",
                "Usuário"
            ),
            email=email,
            picture=data.get(
                "picture"
            ),
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