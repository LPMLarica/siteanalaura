from database.database import SessionLocal

from database.models import Patient
from database.models import Consultation


def create_patient(name, phone, email):

    db = SessionLocal()

    patient = Patient(
        full_name=name,
        phone=phone,
        email=email
    )

    db.add(patient)

    db.commit()

    db.refresh(patient)

    db.close()

    return patient


def get_patients():

    db = SessionLocal()

    patients = db.query(Patient).all()

    db.close()

    return patients


def create_consultation(
        patient_id,
        user_id,
        date,
        hour,
        observation,
        status="Agendada"
):

    db = SessionLocal()

    consultation = Consultation(

        patient_id=patient_id,

        user_id=user_id,

        consultation_date=date,

        consultation_time=hour,

        observation=observation,

        status=status

    )

    db.add(consultation)

    db.commit()

    db.refresh(consultation)

    db.close()

    return consultation


def list_consultations():

    db = SessionLocal()

    data = db.query(Consultation).all()

    db.close()

    return data