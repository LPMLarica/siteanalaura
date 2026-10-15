"""
Pagamentos — no máximo um por consulta (criado/atualizado via upsert).

Regras do financeiro:
- "Recebido no mês": pagamentos com status Pago e data de pagamento no mês;
- "A receber": consultas Realizadas (ou Falta cobrada) sem pagamento Pago.
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from dados.database import session_scope
from dados.models import Consultation, Patient, Payment, User
from utils.formatting import today

STATUS_PAGO = "Pago"
STATUS_PENDENTE = "Pendente"

BILLABLE_STATUSES = ("Realizada", "Falta")


def suggested_amount(db, consultation):
    """Valor da consulta: pagamento existente > valor do paciente > padrão."""

    if consultation.payment and consultation.payment.amount:
        return Decimal(consultation.payment.amount)

    patient = consultation.patient or db.get(Patient, consultation.patient_id)

    if patient and patient.session_value:
        return Decimal(patient.session_value)

    user = db.get(User, consultation.user_id)

    if user and user.default_session_value:
        return Decimal(user.default_session_value)

    return Decimal("0")


def suggested_amount_for(consultation_id, user_id):
    with session_scope() as db:
        consultation = db.scalar(
            select(Consultation)
            .options(joinedload(Consultation.patient), joinedload(Consultation.payment))
            .where(Consultation.id == consultation_id, Consultation.user_id == user_id)
        )
        return suggested_amount(db, consultation) if consultation else Decimal("0")


def upsert_payment(consultation_id, user_id, status, amount=None, payment_method=None, payment_date=None, notes=None):
    with session_scope() as db:
        consultation = db.scalar(
            select(Consultation)
            .options(joinedload(Consultation.payment), joinedload(Consultation.patient))
            .where(Consultation.id == consultation_id, Consultation.user_id == user_id)
        )

        if consultation is None:
            raise ValueError("Consulta não encontrada.")

        payment = consultation.payment

        if payment is None:
            payment = Payment(
                user_id=user_id,
                patient_id=consultation.patient_id,
                consultation_id=consultation.id,
                amount=suggested_amount(db, consultation),
            )
            db.add(payment)

        payment.status = status

        if amount is not None:
            payment.amount = Decimal(str(amount))

        if payment_method is not None:
            payment.payment_method = payment_method

        if notes is not None:
            payment.notes = notes.strip() or None

        if status == STATUS_PAGO:
            payment.payment_date = payment_date or payment.payment_date or today()
        else:
            payment.payment_date = None

        db.flush()
        return payment


def mark_as_paid(consultation_id, user_id, amount, payment_method, payment_date=None, notes=None):
    return upsert_payment(
        consultation_id, user_id, STATUS_PAGO,
        amount=amount, payment_method=payment_method, payment_date=payment_date, notes=notes,
    )


def mark_as_pending(consultation_id, user_id, amount=None):
    return upsert_payment(consultation_id, user_id, STATUS_PENDENTE, amount=amount)


def financial_rows(user_id, start, end):
    """
    Linhas do financeiro de um período: todas as consultas (exceto
    canceladas) com o valor e a situação do pagamento.
    """

    with session_scope() as db:
        consultations = db.scalars(
            select(Consultation)
            .options(joinedload(Consultation.patient), joinedload(Consultation.payment))
            .where(
                Consultation.user_id == user_id,
                Consultation.date >= start,
                Consultation.date <= end,
                Consultation.status != "Cancelada",
            )
            .order_by(Consultation.date, Consultation.start_time)
        ).unique().all()

        rows = []

        for item in consultations:
            payment = item.payment
            paid = bool(payment and payment.status == STATUS_PAGO)

            rows.append(
                {
                    "consultation_id": item.id,
                    "date": item.date,
                    "start_time": item.start_time,
                    "patient": item.patient.full_name,
                    "patient_id": item.patient_id,
                    "status": item.status,
                    "amount": suggested_amount(db, item),
                    "paid": paid,
                    "payment_method": payment.payment_method if payment else None,
                    "payment_date": payment.payment_date if payment else None,
                    "billable": item.status in BILLABLE_STATUSES,
                }
            )

        return rows


def received_between(user_id, start, end):
    with session_scope() as db:
        payments = db.scalars(
            select(Payment).where(
                Payment.user_id == user_id,
                Payment.status == STATUS_PAGO,
                Payment.payment_date >= start,
                Payment.payment_date <= end,
            )
        ).all()

        return sum((Decimal(p.amount or 0) for p in payments), Decimal("0"))


def outstanding(user_id, patient_id=None):
    """Consultas realizadas/faltas ainda sem pagamento (todas as datas)."""

    with session_scope() as db:
        query = (
            select(Consultation)
            .options(joinedload(Consultation.patient), joinedload(Consultation.payment))
            .where(
                Consultation.user_id == user_id,
                Consultation.status.in_(BILLABLE_STATUSES),
                Consultation.date <= today(),
            )
            .order_by(Consultation.date)
        )

        if patient_id:
            query = query.where(Consultation.patient_id == patient_id)

        items = []

        for item in db.scalars(query).unique().all():
            if item.payment and item.payment.status == STATUS_PAGO:
                continue

            items.append(
                {
                    "consultation_id": item.id,
                    "date": item.date,
                    "patient": item.patient.full_name,
                    "patient_id": item.patient_id,
                    "status": item.status,
                    "amount": suggested_amount(db, item),
                }
            )

        return items


def patient_payment_summary(patient_id, user_id):
    with session_scope() as db:
        payments = db.scalars(
            select(Payment).where(
                Payment.patient_id == patient_id,
                Payment.user_id == user_id,
                Payment.status == STATUS_PAGO,
            )
        ).all()

        total_paid = sum((Decimal(p.amount or 0) for p in payments), Decimal("0"))

    pending = outstanding(user_id, patient_id=patient_id)

    return {
        "total_pago": total_paid,
        "total_pendente": sum((row["amount"] for row in pending), Decimal("0")),
        "sessoes_pendentes": len(pending),
    }
