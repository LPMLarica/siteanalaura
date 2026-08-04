from database.database import SessionLocal

from database.models import Consultation



def get_calendar_events(
        user_id
):


    db = SessionLocal()


    consultations = (

        db.query(
            Consultation
        )

        .filter(

            Consultation.user_id
            ==
            user_id

        )

        .all()

    )


    events = []


    for item in consultations:


        events.append(

        {

            "id":
                str(item.id),

            "title":
                f"{item.title} - {item.patient.full_name}",

            "start":
                f"{item.date}T{item.start_time}",

            "end":
                f"{item.date}T{item.end_time}",

            "color":
                item.color,

            "extendedProps":
                {
                    "status":
                        item.status,
                    "observation":
                        item.observation
                }

            }

    )
    db.close()


    return events