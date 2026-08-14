import datetime
import pytz
import json
import requests
import google.oauth2.credentials
import google.auth.transport.requests
from dados.database import SessionLocal
from dados.models import Consultation
import os
import sys
from services.schedule_service import check_schedule_conflict
from services.google_calendar_service import (
    create_google_event
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def create_consultation(data, credentials):

    conflict = check_schedule_conflict(
        data["user_id"],
        data["date"],
        data["start_time"],
        data["end_time"]
    )

    if conflict:
        raise Exception("Já existe uma consulta neste horário.")


    db = SessionLocal()

    consultation = Consultation(**data)

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Sincroniza com o Google Calendar (se o usuário conectou a conta Google)
    # antes de fechar a sessão, para o ID do evento ser persistido corretamente.
    if credentials:
        try:
            event_id = create_google_event(
                credentials,
                consultation
            )
            consultation.google_event_id = event_id
            db.commit()
            db.refresh(consultation)
        except Exception:
            # Não impede o agendamento local caso a sincronização falhe
            # (ex: token expirado, sem internet, permissão revogada).
            db.rollback()

    db.close()

    return consultation


def get_consultation(consultation_id):


    db = SessionLocal()

    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == consultation_id)
        .first()
    )


    db.close()

    return consultation

STATUS_COLORS = {


    "Agendada":

    "#D98CA8",

    "Confirmada":

    "#A8D5BA",

    "Cancelada":

    "#F4C2C2",

    "Remarcada":

    "#DCCDF7"

}



def update_status_color(status):

    return STATUS_COLORS.get(
        status,
        "#D98CA8"
    )

def update_consultation (consultation_id, data):

    db = SessionLocal()


    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == consultation_id)
        .first()
    )


    if not consultation:
        db.close()
        return None



    for key,value in data.items():setattr(
        consultation,
        key,
        value
    )

    db.commit()
    db.refresh (consultation)
    db.close()

    return consultation


def reschedule_consultation(consultation_id,user_id,new_date,new_start,new_end):

    conflict = check_schedule_conflict(
        user_id,
        new_date,
        new_start,
        new_end,
        ignore_id=consultation_id
    )

    if conflict:
        raise Exception("Existe outra consulta neste horário.")

    db = SessionLocal()

    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == consultation_id)
        .first()
    )


    if not consultation:
        db.close()
        return None


    consultation.date = new_date
    consultation.start_time = new_start
    consultation.end_time = new_end
    consultation.status = "Remarcada"
    consultation.color = "#DCCDF7"


    db.commit()
    db.refresh(consultation)
    db.close()


    return consultation

def delete_consultation(consultation_id):

    db = SessionLocal()


    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == consultation_id)
        .first()
    )


    if consultation:
        db.delete(consultation)
        db.commit()
        db.close()