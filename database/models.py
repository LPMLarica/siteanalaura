import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time
)
from sqlalchemy.orm import relationship

from database.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class User(Base, TimestampMixin):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), unique=True, default=generate_uuid)

    google_id = Column(String(200), unique=True)

    name = Column(String(200))

    email = Column(String(200), unique=True)

    picture = Column(Text)

    active = Column(Boolean, default=True)

    consultations = relationship(
        "Consultation",
        back_populates="user"
    )


class Patient(Base, TimestampMixin):

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), unique=True, default=generate_uuid)

    full_name = Column(String(200))

    phone = Column(String(30))

    email = Column(String(200))

    birth_date = Column(Date)

    notes = Column(Text)

    consultations = relationship(
        "Consultation",
        back_populates="patient"
    )


class Availability(Base):

    __tablename__ = "availability"

    id = Column(Integer, primary_key=True)

    weekday = Column(Integer)

    start_time = Column(Time)

    end_time = Column(Time)

    active = Column(Boolean, default=True)


class BlockedDate(Base):

    __tablename__ = "blocked_dates"

    id = Column(Integer, primary_key=True)

    date = Column(Date)

    reason = Column(String(255))


class Consultation(Base, TimestampMixin):

    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), unique=True, default=generate_uuid)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id")
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    consultation_date = Column(Date)

    consultation_time = Column(Time)

    duration = Column(Integer, default=50)

    status = Column(
        String(30),
        default="Agendada"
    )

    confirmed = Column(
        Boolean,
        default=False
    )

    google_event_id = Column(String(255))

    observation = Column(Text)

    patient = relationship(
        "Patient",
        back_populates="consultations"
    )

    user = relationship(
        "User",
        back_populates="consultations"
    )


class Configuration(Base):

    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True)

    timezone = Column(String(100))

    notification_minutes = Column(Integer)

    theme = Column(String(50))