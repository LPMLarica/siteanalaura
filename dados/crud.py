import dados
from dados import SessionLocal
from dados.models import ClinicalRecord
from dados.models import User
from dados.models import AuditLog
from dados.models import Configuration
from dados.models import Patient
from dados.models import Consultation
from dados.models import BlockedDate

from dados.models import (
    Consultation,
    Patient
)


class DatabaseManager:

    def __init__(self):

        self.db = dados.SessionLocal()

    def close(self):

        self.db.close()

    #########################################

    def create_patient(

        self,

        name,

        phone,

        email,

        birth_date=None,

        notes=None

    ):

        patient = Patient(

            full_name=name,

            phone=phone,

            email=email,

            birth_date=birth_date,

            notes=notes

        )

        self.db.add(patient)

        self.db.commit()

        self.db.refresh(patient)

        return patient

    #########################################

    def list_patients(self):

        return (

            self.db

            .query(Patient)

            .order_by(Patient.full_name)

            .all()

        )

    #########################################

    def get_patient(self, patient_id):

        return (

            self.db

            .query(Patient)

            .filter(

                Patient.id == patient_id

            )

            .first()

        )

    #########################################

    def create_consultation(

        self,

        patient_id,

        user_id,

        date,

        hour,

        duration,

        observation

    ):

        consultation = Consultation(

            patient_id=patient_id,

            user_id=user_id,

            consultation_date=date,

            consultation_time=hour,

            duration=duration,

            observation=observation

        )

        self.db.add(consultation)

        self.db.commit()

        self.db.refresh(consultation)

        return consultation

    #########################################

    def list_consultations(self):

        return (

            self.db

            .query(Consultation)

            .order_by(

                Consultation.consultation_date,

                Consultation.consultation_time

            )

            .all()

        )

    #########################################

    def get_consultation(self, consultation_id):

        return (

            self.db

            .query(Consultation)

            .filter(

                Consultation.id == consultation_id

            )

            .first()

        )

    #########################################


    def update_consultation(self, consultation_id, data):

        consultation = self.get_consultation(consultation_id)

        if consultation:

            for key, value in data.items():

                setattr(consultation, key, value)

            self.db.commit()

            self.db.refresh(consultation)

        return consultation

    #########################################

    def delete_consultation(self, consultation_id):

        consultation = self.get_consultation(consultation_id)

        if consultation:

            self.db.delete(consultation)

            self.db.commit()

        return consultation

    #########################################



    def close(self):

        self.db.close()

        return

    #########################################

    def __del__(self):

        self.close()

        return

    #########################################

    def __enter__(self):

        return self

    #########################################

    def __exit__(self, exc_type, exc_value, traceback):

        self.close()

        return
