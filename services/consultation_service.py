from dados.database import SessionLocal
from dados.models import Consultation
from services.schedule_service import check_schedule_conflict


# Campos que quem chama create_consultation pode definir. Evita que um
# dict de dados extra (ex.: vindo de um formulário) sobrescreva colunas
# que não deveriam ser definidas diretamente (ex.: id).
CREATABLE_CONSULTATION_FIELDS = {
    "patient_id",
    "user_id",
    "date",
    "start_time",
    "end_time",
    "title",
    "status",
    "color",
    "observation",
    "confirmed",
}

# Campos que update_consultation pode alterar. Mantém user_id/patient_id
# fora de alcance de uma atualização parcial (ex.: só trocar o status).
UPDATABLE_CONSULTATION_FIELDS = {
    "date",
    "start_time",
    "end_time",
    "title",
    "status",
    "color",
    "observation",
    "confirmed",
}


def create_consultation(data):

    conflict = check_schedule_conflict(
        data["user_id"],
        data["date"],
        data["start_time"],
        data["end_time"]
    )

    if conflict:
        raise Exception("Já existe uma consulta neste horário.")

    db = SessionLocal()

    consultation = Consultation(
        **{
            key: value
            for key, value in data.items()
            if key in CREATABLE_CONSULTATION_FIELDS
        }
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    db.close()

    return consultation


def get_consultation(consultation_id, user_id):
    """Busca uma consulta, restrita ao usuário dono dela — impede que
    um usuário veja/edite a consulta de outro só trocando o id."""

    db = SessionLocal()

    consultation = (
        db.query(Consultation)
        .filter(
            Consultation.id == consultation_id,
            Consultation.user_id == user_id
        )
        .first()
    )

    db.close()

    return consultation


STATUS_COLORS = {

    "Agendada":
    "#D98CA8",

    "Confirmada":
    "#A8D5BA",

    "Cancelada":
    "#F4C2C2",

    "Remarcada":
    "#DCCDF7"

}


def update_status_color(status):

    return STATUS_COLORS.get(
        status,
        "#D98CA8"
    )


def update_consultation(consultation_id, user_id, data):
    """Atualiza uma consulta, restrita ao usuário dono dela e a um
    conjunto de campos permitidos (UPDATABLE_CONSULTATION_FIELDS)."""

    db = SessionLocal()

    consultation = (
        db.query(Consultation)
        .filter(
            Consultation.id == consultation_id,
            Consultation.user_id == user_id
        )
        .first()
    )

    if not consultation:
        db.close()
        return None

    for key, value in data.items():
        if key not in UPDATABLE_CONSULTATION_FIELDS:
            continue
        setattr(
            consultation,
            key,
            value
        )

    db.commit()
    db.refresh(consultation)
    db.close()

    return consultation


def reschedule_consultation(consultation_id, user_id, new_date, new_start, new_end):

    conflict = check_schedule_conflict(
        user_id,
        new_date,
        new_start,
        new_end,
        ignore_id=consultation_id
    )

    if conflict:
        raise Exception("Existe outra consulta neste horário.")

    db = SessionLocal()

    consultation = (
        db.query(Consultation)
        .filter(
            Consultation.id == consultation_id,
            Consultation.user_id == user_id
        )
        .first()
    )

    if not consultation:
        db.close()
        return None

    consultation.date = new_date
    consultation.start_time = new_start
    consultation.end_time = new_end
    consultation.status = "Remarcada"
    consultation.color = "#DCCDF7"

    db.commit()
    db.refresh(consultation)
    db.close()

    return consultation


def delete_consultation(consultation_id, user_id):
    """Remove uma consulta, restrita ao usuário dono dela."""

    db = SessionLocal()

    try:
        consultation = (
            db.query(Consultation)
            .filter(
                Consultation.id == consultation_id,
                Consultation.user_id == user_id
            )
            .first()
        )

        if consultation:
            db.delete(consultation)
            db.commit()

        return consultation is not None
    finally:
        db.close()
