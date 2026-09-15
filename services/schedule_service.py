from dados.database import SessionLocal
from dados.models import Consultation
from services.availability_service import (
    available_slot
)


def check_schedule_conflict(user_id, date, start_time, end_time, ignore_id=None):

    # Nenhuma consulta ao banco é necessária para esta checagem, então
    # só abrimos a sessão depois de saber que vamos usá-la — evita
    # deixar uma conexão aberta nesse caminho de retorno antecipado.
    if not available_slot(user_id, date, start_time, end_time):
        return True

    db = SessionLocal()

    try:
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
    finally:
        db.close()

    for item in consultations:

        if (start_time < item.end_time and end_time > item.start_time):

            return True

    return False
