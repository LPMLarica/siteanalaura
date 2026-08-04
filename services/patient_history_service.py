from database.database import SessionLocal
from database.models import Consultation


def get_patient_consultations(patient_id):

    db = SessionLocal()

    consultations = (
        db.query(
            Consultation
        )

        .filter(
            Consultation.patient_id == patient_id
        )

        .order_by(
            Consultation.date.desc()
        )

        .all()
    )

    db.close()

    return consultations



def count_patient_consultations(patient_id):

    db = SessionLocal()

    total = (
        db.query(
            Consultation
        )

        .filter(
            Consultation.patient_id == patient_id
        )

        .count()
    )

    db.close()

    return total


def get_next_consultation(patient_id):

    from datetime import date

    db = SessionLocal()

    consultation = (

        db.query(
            Consultation
        )

        .filter(
            Consultation.patient_id == patient_id,
            Consultation.date >= date.today(),
            Consultation.status != "Cancelada"
        )

        .order_by(
            Consultation.date,
            Consultation.start_time
        )

        .first()
    )

    db.close()

    return consultation