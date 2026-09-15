from dados.database import SessionLocal
from dados.models import Patient


# Campos que create_patient pode definir. Evita que um dict de dados
# extra sobrescreva colunas que não deveriam vir do formulário.
PATIENT_FIELDS = {
    "user_id",
    "full_name",
    "cpf",
    "birth_date",
    "phone",
    "email",
    "address",
    "notes",
    "status",
    "photo",
}


def create_patient(data):

    db = SessionLocal()

    patient = Patient(
        **{
            key: value
            for key, value in data.items()
            if key in PATIENT_FIELDS
        }
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


def search_patients(user_id, text):

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


def get_patient(patient_id, user_id):
    """Busca um paciente, restrito ao usuário dono dele — impede que
    um usuário veja o paciente/prontuário de outro só trocando o id."""

    db = SessionLocal()

    patient = (
        db.query(
            Patient
        )

        .filter(
            Patient.id == patient_id,
            Patient.user_id == user_id
        )
        .first()
    )

    db.close()

    return patient
