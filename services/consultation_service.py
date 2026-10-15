from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from dados.database import session_scope
from dados.models import CONSULTATION_STATUSES, MODALITIES, Consultation, Patient
from services.schedule_service import ScheduleError, validate_slot

UPDATABLE_FIELDS = {"title", "status", "modality", "observation"}


def _owned(db, consultation_id, user_id):
    return db.scalar(
        select(Consultation)
        .options(joinedload(Consultation.patient), joinedload(Consultation.payment))
        .where(Consultation.id == consultation_id, Consultation.user_id == user_id)
    )


def get_consultation(consultation_id, user_id):
    with session_scope() as db:
        return _owned(db, consultation_id, user_id)


def create_consultations(
    user_id,
    patient_id,
    day,
    start_time,
    duration_minutes,
    title="Sessão",
    status="Agendada",
    modality="Presencial",
    observation=None,
    repeat_weeks=1,
    force=False,
):
    """
    Cria a consulta (e as repetições semanais, se ``repeat_weeks`` > 1).
    Tudo ou nada: se qualquer data der conflito, nada é gravado.
    """

    if status not in CONSULTATION_STATUSES:
        raise ScheduleError("Status inválido.")

    if modality not in MODALITIES:
        raise ScheduleError("Modalidade inválida.")

    start_dt = datetime.combine(day, start_time)
    end_time = (start_dt + timedelta(minutes=int(duration_minutes))).time()

    if end_time <= start_time:
        raise ScheduleError("A consulta precisa terminar no mesmo dia.")

    with session_scope() as db:
        patient = db.scalar(
            select(Patient).where(Patient.id == patient_id, Patient.user_id == user_id)
        )

        if patient is None:
            raise ScheduleError("Paciente não encontrado.")

        created = []

        for week in range(max(1, int(repeat_weeks))):
            current = day + timedelta(weeks=week)

            try:
                validate_slot(db, user_id, current, start_time, end_time, force=force)
            except ScheduleError as error:
                if week == 0:
                    raise
                raise ScheduleError(f"Repetição de {current:%d/%m/%Y}: {error}", soft=error.soft) from error

            consultation = Consultation(
                user_id=user_id,
                patient_id=patient_id,
                date=current,
                start_time=start_time,
                end_time=end_time,
                title=(title or "Sessão").strip() or "Sessão",
                status=status,
                modality=modality,
                observation=(observation or "").strip() or None,
            )
            db.add(consultation)
            created.append(consultation)

        db.flush()

        return created


def update_consultation(consultation_id, user_id, data):
    with session_scope() as db:
        consultation = _owned(db, consultation_id, user_id)

        if consultation is None:
            return None

        for key, value in data.items():
            if key in UPDATABLE_FIELDS:
                if isinstance(value, str):
                    value = value.strip() or None
                setattr(consultation, key, value)

        if not consultation.title:
            consultation.title = "Sessão"

        db.flush()
        return consultation


def reschedule_consultation(consultation_id, user_id, new_date, new_start, new_end, force=False):
    with session_scope() as db:
        consultation = _owned(db, consultation_id, user_id)

        if consultation is None:
            raise ScheduleError("Consulta não encontrada.")

        validate_slot(db, user_id, new_date, new_start, new_end, ignore_id=consultation_id, force=force)

        consultation.date = new_date
        consultation.start_time = new_start
        consultation.end_time = new_end

        db.flush()
        return consultation


def delete_consultation(consultation_id, user_id):
    with session_scope() as db:
        consultation = db.scalar(
            select(Consultation).where(
                Consultation.id == consultation_id, Consultation.user_id == user_id
            )
        )

        if consultation is None:
            return False

        db.delete(consultation)
        return True


def list_consultations(user_id, start=None, end=None, patient_id=None, statuses=None):
    with session_scope() as db:
        query = (
            select(Consultation)
            .options(joinedload(Consultation.patient), joinedload(Consultation.payment))
            .where(Consultation.user_id == user_id)
        )

        if start:
            query = query.where(Consultation.date >= start)

        if end:
            query = query.where(Consultation.date <= end)

        if patient_id:
            query = query.where(Consultation.patient_id == patient_id)

        if statuses:
            query = query.where(Consultation.status.in_(statuses))

        return db.scalars(
            query.order_by(Consultation.date, Consultation.start_time)
        ).unique().all()


def calendar_events(user_id, start, end, hide_cancelled=False):
    events = []

    for item in list_consultations(user_id, start, end):
        if hide_cancelled and item.status == "Cancelada":
            continue

        paid = bool(item.payment and item.payment.status == "Pago")
        prefix = "✓ " if paid else ""

        events.append(
            {
                "id": str(item.id),
                "title": f"{prefix}{item.patient.full_name}",
                # Horário "de parede" (sem fuso): o calendário roda em UTC
                # para não deslocar nada pelo fuso do navegador.
                "start": f"{item.date.isoformat()}T{item.start_time:%H:%M:%S}",
                "end": f"{item.date.isoformat()}T{item.end_time:%H:%M:%S}",
                "backgroundColor": item.color,
                "borderColor": item.color,
                "textColor": "#FFFFFF",
                "editable": item.status not in ("Realizada", "Cancelada"),
                "extendedProps": {
                    "status": item.status,
                    "modality": item.modality,
                },
            }
        )

    return events
