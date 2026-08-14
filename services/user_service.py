from dados.database import SessionLocal

from dados.models import User



def get_or_create_user(data):

    db = SessionLocal()

    user = (
        db.query(User)
        .filter(
            User.email ==
            data["email"]
        )
        .first()
    )

    if not user:

        user = User(
            client_id=data["client_id"],
            name=data["name"],
            email=data["email"],
            picture=data["picture"]
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    db.close()


    return user