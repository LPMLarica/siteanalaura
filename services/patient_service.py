from database.database import SessionLocal
from database.models import Patient


def create_patient(data):

    db = SessionLocal()

    patient = Patient(
        **data
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)
    db.close()

    return patient


def get_patients(user_id):


    db = SessionLocal()

    patients = (

        db.query(
            Patient
        )

        .filter(
            Patient.user_id == user_id
        )

        .order_by(
            Patient.full_name
        )

        .all()
    )

    db.close()

    return patients


def search_patients(user_id,text):

    db = SessionLocal()

    result = (

        db.query(
            Patient
        )

        .filter(
            Patient.user_id == user_id,
            Patient.full_name.ilike(
                f"%{text}%"
            )
        )

        .all()
    )

    db.close()

    return result


def get_patient(patient_id):

    db = SessionLocal()


    patient = (
        db.query(
            Patient
        )

        .filter(
            Patient.id == patient_id
        )
        .first()
    )

    db.close()

    return patient