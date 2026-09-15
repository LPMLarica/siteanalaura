"""
Controle de pagamentos, correlacionado a paciente + consulta.

Cada consulta pode ter, no máximo, um registro de pagamento
(services.payment_service usa upsert_payment: cria se não existir,
atualiza se já existir). O status ("Pago"/"Pendente") é o que
alimenta o indicador exibido no perfil do paciente e nos detalhes da
consulta.
"""

from datetime import date

from dados.database import SessionLocal
from dados.models import Payment


STATUS_PAGO = "Pago"
STATUS_PENDENTE = "Pendente"

PAYMENT_METHODS = [
    "Pix",
    "Cartão",
    "Dinheiro",
    "Transferência",
    "Outro",
]


def get_payment_for_consultation(consultation_id, user_id):
    """Busca o pagamento de uma consulta, restrito ao usuário dono."""

    db = SessionLocal()

    payment = (
        db.query(Payment)
        .filter(
            Payment.consultation_id == consultation_id,
            Payment.user_id == user_id,
        )
        .first()
    )

    db.close()

    return payment


def get_payments_for_patient(patient_id, user_id):
    """Lista os pagamentos de um paciente, restrito ao usuário dono."""

    db = SessionLocal()

    payments = (
        db.query(Payment)
        .filter(
            Payment.patient_id == patient_id,
            Payment.user_id == user_id,
        )
        .order_by(Payment.payment_date.desc())
        .all()
    )

    db.close()

    return payments


def get_patient_payment_summary(patient_id, user_id):
    """Resumo simples (total pago / total pendente / quantidade) para
    exibir no perfil do paciente."""

    payments = get_payments_for_patient(patient_id, user_id)

    total_pago = sum(
        (p.amount or 0) for p in payments if p.status == STATUS_PAGO
    )

    total_pendente = sum(
        (p.amount or 0) for p in payments if p.status != STATUS_PAGO
    )

    return {
        "total_pago": total_pago,
        "total_pendente": total_pendente,
        "quantidade": len(payments),
    }


def upsert_payment(
    consultation_id,
    patient_id,
    user_id,
    status,
    amount=None,
    payment_method=None,
    notes=None,
    payment_date=None,
):
    """Cria ou atualiza o pagamento associado a uma consulta.

    Sempre restrito ao user_id de quem está chamando — nunca cria/edita
    o pagamento de uma consulta de outro usuário.
    """

    db = SessionLocal()

    try:
        payment = (
            db.query(Payment)
            .filter(
                Payment.consultation_id == consultation_id,
                Payment.user_id == user_id,
            )
            .first()
        )

        if payment is None:
            payment = Payment(
                consultation_id=consultation_id,
                patient_id=patient_id,
                user_id=user_id,
            )
            db.add(payment)

        payment.status = status

        if amount is not None:
            payment.amount = amount

        if payment_method is not None:
            payment.payment_method = payment_method

        if notes is not None:
            payment.notes = notes

        payment.payment_date = payment_date or date.today()

        db.commit()
        db.refresh(payment)

        return payment
    finally:
        db.close()


def mark_as_paid(consultation_id, patient_id, user_id, amount, payment_method, notes=None):

    return upsert_payment(
        consultation_id=consultation_id,
        patient_id=patient_id,
        user_id=user_id,
        status=STATUS_PAGO,
        amount=amount,
        payment_method=payment_method,
        notes=notes,
    )


def mark_as_pending(consultation_id, patient_id, user_id, notes=None):

    return upsert_payment(
        consultation_id=consultation_id,
        patient_id=patient_id,
        user_id=user_id,
        status=STATUS_PENDENTE,
        notes=notes,
    )
