"""Prontuário: evoluções de sessão, sempre criptografadas no banco."""

from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import select

from dados.database import session_scope
from dados.models import ClinicalRecord, Consultation
from security.encryption import decrypt_text, encrypt_text


@dataclass
class RecordView:
    id: int
    session_date: date
    content: str
    consultation_id: int | None
    created_at: datetime
    updated_at: datetime


def _view(record):
    return RecordView(
        id=record.id,
        session_date=record.session_date,
        content=decrypt_text(record.content),
        consultation_id=record.consultation_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def create_record(user_id, patient_id, session_date, content, consultation_id=None):
    content = (content or "").strip()

    if not content:
        raise ValueError("Escreva o registro da sessão.")

    with session_scope() as db:
        if consultation_id:
            owned = db.scalar(
                select(Consultation.id).where(
                    Consultation.id == consultation_id,
                    Consultation.user_id == user_id,
                    Consultation.patient_id == patient_id,
                )
            )
            consultation_id = owned

        record = ClinicalRecord(
            user_id=user_id,
            patient_id=patient_id,
            consultation_id=consultation_id,
            session_date=session_date,
            content=encrypt_text(content),
        )
        db.add(record)
        db.flush()

        return _view(record)


def update_record(record_id, user_id, content, session_date=None):
    content = (content or "").strip()

    if not content:
        raise ValueError("O registro não pode ficar vazio.")

    with session_scope() as db:
        record = db.scalar(
            select(ClinicalRecord).where(
                ClinicalRecord.id == record_id, ClinicalRecord.user_id == user_id
            )
        )

        if record is None:
            raise ValueError("Registro não encontrado.")

        record.content = encrypt_text(content)

        if session_date:
            record.session_date = session_date

        db.flush()
        return _view(record)


def list_records(patient_id, user_id):
    with session_scope() as db:
        records = db.scalars(
            select(ClinicalRecord)
            .where(
                ClinicalRecord.patient_id == patient_id,
                ClinicalRecord.user_id == user_id,
            )
            .order_by(ClinicalRecord.session_date.desc(), ClinicalRecord.created_at.desc())
        ).all()

        return [_view(record) for record in records]


def consultations_with_record(patient_id, user_id):
    with session_scope() as db:
        return set(
            db.scalars(
                select(ClinicalRecord.consultation_id).where(
                    ClinicalRecord.patient_id == patient_id,
                    ClinicalRecord.user_id == user_id,
                    ClinicalRecord.consultation_id.is_not(None),
                )
            ).all()
        )
