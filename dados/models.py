"""
Modelos do banco de dados.

Todos os registros pertencem a um usuário (``user_id``) — cada
profissional só enxerga os próprios pacientes, consultas, prontuários e
pagamentos. Os serviços em ``services/`` sempre filtram por ``user_id``.
"""

from datetime import date, datetime, time, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dados.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


# ---------------------------------------------------------------- usuários


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # ID do usuário no Supabase Auth (auth.users.id).
    supabase_uid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    professional_register: Mapped[str | None] = mapped_column(String(50))  # CRP
    phone: Mapped[str | None] = mapped_column(String(30))

    default_session_minutes: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    default_session_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# --------------------------------------------------------------- pacientes


PATIENT_STATUSES = ["Ativo", "Em pausa", "Alta", "Inativo"]


class Patient(TimestampMixin, Base):
    __tablename__ = "patients"
    __table_args__ = (Index("ix_patients_user_name", "user_id", "full_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    cpf: Mapped[str | None] = mapped_column(String(14))
    birth_date: Mapped[date | None] = mapped_column(Date)
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(150))
    address: Mapped[str | None] = mapped_column(String(255))
    emergency_contact: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="Ativo", nullable=False)
    session_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    consultations: Mapped[list["Consultation"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan", passive_deletes=True
    )
    records: Mapped[list["ClinicalRecord"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan", passive_deletes=True
    )


# --------------------------------------------------------------- consultas


CONSULTATION_STATUSES = ["Agendada", "Confirmada", "Realizada", "Falta", "Cancelada"]

STATUS_COLORS = {
    "Agendada": "#7D9FC3",
    "Confirmada": "#4F7CAC",
    "Realizada": "#5E9C7F",
    "Falta": "#C9894B",
    "Cancelada": "#B7AFB3",
}

MODALITIES = ["Presencial", "Online"]


class Consultation(TimestampMixin, Base):
    __tablename__ = "consultations"
    __table_args__ = (Index("ix_consultations_user_date", "user_id", "date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )

    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    title: Mapped[str] = mapped_column(String(255), default="Sessão", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="Agendada", nullable=False)
    modality: Mapped[str] = mapped_column(String(30), default="Presencial", nullable=False)
    observation: Mapped[str | None] = mapped_column(Text)

    patient: Mapped["Patient"] = relationship(back_populates="consultations")
    payment: Mapped["Payment | None"] = relationship(
        back_populates="consultation",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def color(self):
        return STATUS_COLORS.get(self.status, STATUS_COLORS["Agendada"])


# ------------------------------------------------------------- pagamentos


PAYMENT_STATUSES = ["Pago", "Pendente"]
PAYMENT_METHODS = ["Pix", "Cartão de crédito", "Cartão de débito", "Dinheiro", "Transferência", "Convênio", "Outro"]


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("consultation_id", name="uq_payments_consultation"),
        Index("ix_payments_user_date", "user_id", "payment_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    consultation_id: Mapped[int] = mapped_column(
        ForeignKey("consultations.id", ondelete="CASCADE"), nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(50))
    payment_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="Pendente", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    consultation: Mapped["Consultation"] = relationship(back_populates="payment")


# -------------------------------------------------------------- prontuário


class ClinicalRecord(TimestampMixin, Base):
    __tablename__ = "clinical_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    consultation_id: Mapped[int | None] = mapped_column(
        ForeignKey("consultations.id", ondelete="SET NULL"), index=True
    )

    session_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Texto criptografado (Fernet) — ver security/encryption.py.
    content: Mapped[str] = mapped_column(Text, nullable=False)

    patient: Mapped["Patient"] = relationship(back_populates="records")


# -------------------------------------------------- horários e bloqueios


WEEKDAYS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


class WorkingHours(Base):
    __tablename__ = "working_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 = segunda
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class BlockedPeriod(Base):
    __tablename__ = "blocked_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255))


# -------------------------------------------------------------- auditoria


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    target: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
