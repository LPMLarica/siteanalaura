from database.database import SessionLocal

from database.models import User



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

            google_id=data["google_id"],

            name=data["name"],

            email=data["email"],

            picture=data["picture"]

        )


        db.add(user)

        db.commit()

        db.refresh(user)



    db.close()


    return user