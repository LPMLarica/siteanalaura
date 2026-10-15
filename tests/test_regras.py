"""Testes das regras principais (rodam com SQLite temporário)."""

import os
import sys
from datetime import time, timedelta
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    db = tmp_path_factory.mktemp("db") / "test.db"
    os.environ.update(
        DATABASE_URL=os.environ.get("TEST_DATABASE_URL") or f"sqlite:///{db}",
        SUPABASE_URL="https://example.supabase.co",
        SUPABASE_KEY="sb_publishable_test",
        SECRET_KEY=Fernet.generate_key().decode(),
    )

    from dados.database import init_db
    from services.user_service import get_or_create_user

    init_db()
    user = get_or_create_user({"supabase_uid": "u1", "email": "a@ex.com", "name": "Ana"})
    other = get_or_create_user({"supabase_uid": "u2", "email": "b@ex.com", "name": "Bia"})
    return user, other


def test_conflito_e_isolamento(env):
    from services.consultation_service import create_consultations, get_consultation
    from services.patient_service import create_patient, get_patient
    from services.schedule_service import ScheduleError
    from utils.formatting import today

    user, other = env
    patient = create_patient(user["id"], {"full_name": "Maria"})
    day = today() + timedelta(days=3)

    created = create_consultations(user["id"], patient.id, day, time(9, 0), 50, repeat_weeks=3)
    assert len(created) == 3
    assert created[2].date == day + timedelta(weeks=2)

    with pytest.raises(ScheduleError):
        create_consultations(user["id"], patient.id, day, time(9, 30), 50)

    # outro usuário não enxerga paciente nem consulta
    assert get_patient(patient.id, other["id"]) is None
    assert get_consultation(created[0].id, other["id"]) is None


def test_horario_de_atendimento_e_bloqueio(env):
    from services.consultation_service import create_consultations
    from services.patient_service import create_patient
    from services.schedule_service import ScheduleError, add_blocked_period, add_working_hours
    from utils.formatting import today

    _, user = env
    patient = create_patient(user["id"], {"full_name": "João"})

    # sem horários cadastrados, qualquer horário é aceito
    day = today() + timedelta(days=10)
    create_consultations(user["id"], patient.id, day, time(21, 0), 50)

    add_working_hours(user["id"], list(range(7)), time(8, 0), time(12, 0))

    with pytest.raises(ScheduleError) as info:
        create_consultations(user["id"], patient.id, day, time(15, 0), 50)
    assert info.value.soft

    create_consultations(user["id"], patient.id, day, time(15, 0), 50, force=True)

    add_blocked_period(user["id"], day + timedelta(days=1), day + timedelta(days=1), "Feriado")

    with pytest.raises(ScheduleError) as info:
        create_consultations(user["id"], patient.id, day + timedelta(days=1), time(9, 0), 50, force=True)
    assert not info.value.soft


def test_prontuario_criptografado(env):
    from sqlalchemy import select

    from dados.database import session_scope
    from dados.models import ClinicalRecord
    from services.clinical_record_service import create_record, list_records
    from services.patient_service import create_patient
    from utils.formatting import today

    user, _ = env
    patient = create_patient(user["id"], {"full_name": "Paciente Sigilo"})
    create_record(user["id"], patient.id, today(), "texto confidencial")

    with session_scope() as db:
        raw = db.scalar(select(ClinicalRecord.content).where(ClinicalRecord.patient_id == patient.id))

    assert "confidencial" not in raw
    assert list_records(patient.id, user["id"])[0].content == "texto confidencial"


def test_pagamentos(env):
    from decimal import Decimal

    from services.consultation_service import create_consultations, update_consultation
    from services.patient_service import create_patient
    from services.payment_service import mark_as_paid, outstanding, patient_payment_summary
    from utils.formatting import today

    user, _ = env
    patient = create_patient(user["id"], {"full_name": "Pagante", "session_value": Decimal("180")})
    [consultation] = create_consultations(user["id"], patient.id, today() - timedelta(days=20), time(7, 0), 50, force=True)
    update_consultation(consultation.id, user["id"], {"status": "Realizada"})

    pending = outstanding(user["id"], patient_id=patient.id)
    assert pending and pending[0]["amount"] == Decimal("180")

    mark_as_paid(consultation.id, user["id"], 180, "Pix")
    summary = patient_payment_summary(patient.id, user["id"])
    assert summary["total_pago"] == Decimal("180")
    assert summary["sessoes_pendentes"] == 0


def test_cpf():
    from utils.formatting import format_cpf, is_valid_cpf

    assert is_valid_cpf("529.982.247-25")
    assert not is_valid_cpf("111.111.111-11")
    assert format_cpf("52998224725") == "529.982.247-25"
