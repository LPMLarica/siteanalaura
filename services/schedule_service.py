from dados.database import SessionLocal
from dados.models import Consultation
from services.availability_service import (
    available_slot
)


def check_schedule_conflict(user_id,date,start_time,end_time,ignore_id=None):

    db = SessionLocal()

    if not available_slot(user_id,date,start_time,end_time):
    
            return True
    
    query = (

        db.query(Consultation)

        .filter(
            Consultation.user_id == user_id,
            Consultation.date == date
        )
    )

    if ignore_id:

        query = query.filter(
            Consultation.id != ignore_id
        )

    consultations = query.all()

    db.close()


    for item in consultations:

        if (start_time < item.end_time and end_time > item.start_time):

            return True

    return False