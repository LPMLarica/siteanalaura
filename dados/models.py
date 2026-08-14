import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time
)
from sqlalchemy.orm import relationship
import dados.database
from dados.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

class Budget(dados.database.Base):

    __tablename__ = "budgets"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id"
        ),
        nullable=False
    )

    patient_id = Column(
        Integer,
        ForeignKey(
            "patients.id"
        ),
        nullable=False
    )

    description = Column(
        String(255)
    )

    sessions_quantity = Column(
        Integer,
        default=1
    )

    session_value = Column(
        Float,
        default=0
    )

    discount = Column(
        Float,
        default=0
    )

    total_value = Column(
        Float,
        default=0
    )


    status = Column(
        String(50),
        default="Pendente"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    patient = relationship(
        "Patient"
    )

class Payment(dados.database.Base):

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    consultation_id = Column(
        Integer,
        ForeignKey("consultations.id")
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id")
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    amount = Column(Float)

    payment_method = Column(String(50))

    payment_date = Column(Date)

    status = Column(String(30))

    notes = Column(Text)

    receipt_number = Column(String(100))

class WorkingHours(dados.database.Base):

    __tablename__ = "working_hours"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    weekday = Column(
        Integer,
        nullable=False
    )

    start_time = Column(
        Time,
        nullable=False
    )

    end_time = Column(
        Time,
        nullable=False
    )

    active = Column(
        Boolean,
        default=True
    )

class BlockedSchedule(dados.database.Base):

    __tablename__ = "blocked_schedule"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    date = Column(
        Date,
        nullable=False
    )

    reason = Column(
        String(255)
    )

    all_day = Column(
        Boolean,
        default=False
    )

class User(dados.database.Base, TimestampMixin):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=generate_uuid)
    client_id = Column(String(200), unique=True)
    name = Column(String(200))
    email = Column(String(200), unique=True)
    picture = Column(Text)
    active = Column(Boolean, default=True)

    consultations = relationship(
        "Consultation",
        back_populates="user"
    )


class Patient(dados.database.Base):

    __tablename__ = "patients"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    cpf = Column(
        String(14)
    )

    birth_date = Column(
        Date
    )

    phone = Column(
        String(30)
    )

    email = Column(
        String(150)
    )

    address = Column(
        String(255)
    )

    notes = Column(
        Text
    )

    status = Column(
        String(30),
        default="Ativo"
    )

    photo = Column(
        String(500)
    )

    records = relationship(
        "ClinicalRecord",
        back_populates="patient"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    consultations = relationship(
        "Consultation",
        back_populates="patient"
    )

class AuditLog(dados.database.Base):

    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id"
        )
    )

    action = Column(
        String(255)
    )

    target = Column(
        String(255)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

class Availability(dados.database.Base):

    __tablename__ = "availability"

    id = Column(Integer, primary_key=True)
    weekday = Column(Integer)
    start_time = Column(Time)
    end_time = Column(Time)
    active = Column(Boolean, default=True)


class BlockedDate(dados.database.Base):

    __tablename__ = "blocked_dates"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    reason = Column(String(255))


class Consultation(dados.database.Base):

    __tablename__ = "consultations"


    id = Column(
        Integer,
        primary_key=True
    )


    patient_id = Column(
        Integer,
        ForeignKey(
            "patients.id"
        )
    )


    user_id = Column(
        Integer,
        ForeignKey(
            "users.id"
        )
    )


    date = Column(
        Date,
        nullable=False
    )


    start_time = Column(
        Time,
        nullable=False
    )


    end_time = Column(
        Time,
        nullable=False
    )


    title = Column(
        String(255),
        default="Consulta"
    )


    status = Column(
        String(50),
        default="Agendada"
    )


    color = Column(
        String(20),
        default="#D98CA8"
    )


    observation = Column(
        Text
    )


    confirmed = Column(
        Boolean,
        default=False
    )


    google_event_id = Column(
        String(255)
    )


    patient = relationship(
        "Patient",
        back_populates="consultations"
    )


    user = relationship(
        "User",
        back_populates="consultations"
    )



class ClinicalRecord(dados.database.Base):

    __tablename__ = "clinical_records"

    id = Column(
        Integer,
        primary_key=True
    )

    patient_id = Column(
        Integer,
        ForeignKey(
            "patients.id"
        ),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id"
        ),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(

        DateTime,
        default=datetime.utcnow
    )

    patient = relationship(
        "Patient",
        back_populates="records"
    )

    user = relationship(
        "User"
    )

class Configuration(dados.database.Base):

    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True)
    timezone = Column(String(100))
    notification_minutes = Column(Integer)
    theme = Column(String(50))