from sqlalchemy import func, or_, select

from dados.database import session_scope
from dados.models import ClinicalRecord, Consultation, Patient
from utils.formatting import today

PATIENT_FIELDS = {
    "full_name",
    "cpf",
    "birth_date",
    "phone",
    "email",
    "address",
    "emergency_contact",
    "notes",
    "status",
    "session_value",
}


class PatientError(Exception):
    pass


def _clean(data):
    cleaned = {}

    for key, value in data.items():
        if key not in PATIENT_FIELDS:
            continue

        if isinstance(value, str):
            value = value.strip() or None

        cleaned[key] = value

    return cleaned


def list_patients(user_id, search=None, status=None):
    with session_scope() as db:
        query = select(Patient).where(Patient.user_id == user_id)

        if status:
            query = query.where(Patient.status.in_(status if isinstance(status, (list, tuple)) else [status]))

        if search:
            term = f"%{search.strip()}%"
            query = query.where(
                or_(
                    Patient.full_name.ilike(term),
                    Patient.phone.ilike(term),
                    Patient.email.ilike(term),
                    Patient.cpf.ilike(term),
                )
            )

        return db.scalars(query.order_by(func.lower(Patient.full_name))).all()


def get_patient(patient_id, user_id):
    with session_scope() as db:
        return db.scalar(
            select(Patient).where(Patient.id == patient_id, Patient.user_id == user_id)
        )


def create_patient(user_id, data):
    data = _clean(data)

    if not data.get("full_name"):
        raise PatientError("Informe o nome do paciente.")

    with session_scope() as db:
        patient = Patient(user_id=user_id, **data)
        db.add(patient)
        db.flush()
        return patient


def update_patient(patient_id, user_id, data):
    data = _clean(data)

    if "full_name" in data and not data["full_name"]:
        raise PatientError("Informe o nome do paciente.")

    with session_scope() as db:
        patient = db.scalar(
            select(Patient).where(Patient.id == patient_id, Patient.user_id == user_id)
        )

        if patient is None:
            raise PatientError("Paciente não encontrado.")

        for key, value in data.items():
            setattr(patient, key, value)

        db.flush()
        return patient


def delete_patient(patient_id, user_id):
    """
    Exclui o paciente apenas se ele não tiver consultas nem prontuário.
    Com histórico, o caminho correto é mudar o status para "Inativo"
    (o registro documental deve ser guardado — Resolução CFP 001/2009).
    """

    with session_scope() as db:
        patient = db.scalar(
            select(Patient).where(Patient.id == patient_id, Patient.user_id == user_id)
        )

        if patient is None:
            raise PatientError("Paciente não encontrado.")

        has_history = db.scalar(
            select(func.count()).select_from(Consultation).where(Consultation.patient_id == patient_id)
        ) or db.scalar(
            select(func.count()).select_from(ClinicalRecord).where(ClinicalRecord.patient_id == patient_id)
        )

        if has_history:
            raise PatientError(
                "Este paciente tem consultas ou prontuário registrados. "
                "Para preservar o histórico, altere o status para \"Inativo\"."
            )

        db.delete(patient)


def patient_summary(patient_id, user_id):
    """Números do paciente para a ficha."""

    with session_scope() as db:
        rows = db.execute(
            select(Consultation.status, func.count())
            .where(Consultation.patient_id == patient_id, Consultation.user_id == user_id)
            .group_by(Consultation.status)
        ).all()

        counts = {status: total for status, total in rows}

        next_consultation = db.scalar(
            select(Consultation)
            .where(
                Consultation.patient_id == patient_id,
                Consultation.user_id == user_id,
                Consultation.date >= today(),
                Consultation.status.in_(["Agendada", "Confirmada"]),
            )
            .order_by(Consultation.date, Consultation.start_time)
            .limit(1)
        )

        last_session = db.scalar(
            select(func.max(Consultation.date)).where(
                Consultation.patient_id == patient_id,
                Consultation.user_id == user_id,
                Consultation.status == "Realizada",
            )
        )

    return {
        "realizadas": counts.get("Realizada", 0),
        "faltas": counts.get("Falta", 0),
        "canceladas": counts.get("Cancelada", 0),
        "agendadas": counts.get("Agendada", 0) + counts.get("Confirmada", 0),
        "proxima": next_consultation,
        "ultima": last_session,
    }
