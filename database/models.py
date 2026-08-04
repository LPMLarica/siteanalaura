from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import Time
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Text

from sqlalchemy.orm import relationship

from datetime import datetime

from database.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    google_id = Column(String, unique=True)

    name = Column(String)

    email = Column(String, unique=True)

    picture = Column(String)

    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    consultations = relationship("Consultation", back_populates="user")


class Patient(Base):

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)

    full_name = Column(String)

    phone = Column(String)

    email = Column(String)

    birth_date = Column(Date)

    created_at = Column(DateTime, default=datetime.utcnow)

    consultations = relationship("Consultation", back_populates="patient")


class Consultation(Base):

    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True)

    patient_id = Column(Integer, ForeignKey("patients.id"))

    user_id = Column(Integer, ForeignKey("users.id"))

    consultation_date = Column(Date)

    consultation_time = Column(Time)

    observation = Column(Text)

    status = Column(String)

    google_event_id = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="consultations")

    user = relationship("User", back_populates="consultations")


class Configuration(Base):

    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True)

    timezone = Column(String)

    notification_minutes = Column(Integer)

    theme = Column(String)