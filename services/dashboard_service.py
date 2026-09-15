from datetime import date, timedelta

from dados.database import SessionLocal
from dados.models import Consultation, Patient


def get_dashboard_stats(user_id):
    """Números reais (não mais fixos em '0') para os cards do
    dashboard, e a lista das próximas consultas do usuário logado."""

    db = SessionLocal()

    try:
        today = date.today()
        week_end = today + timedelta(days=7)

        consultas_hoje = (
            db.query(Consultation)
            .filter(
                Consultation.user_id == user_id,
                Consultation.date == today,
                Consultation.status != "Cancelada",
            )
            .count()
        )

        consultas_semana = (
            db.query(Consultation)
            .filter(
                Consultation.user_id == user_id,
                Consultation.date >= today,
                Consultation.date <= week_end,
                Consultation.status != "Cancelada",
            )
            .count()
        )

        total_pacientes = (
            db.query(Patient)
            .filter(Patient.user_id == user_id)
            .count()
        )

        proxima = (
            db.query(Consultation)
            .filter(
                Consultation.user_id == user_id,
                Consultation.date >= today,
                Consultation.status != "Cancelada",
            )
            .order_by(Consultation.date, Consultation.start_time)
            .first()
        )

        proxima_label = "--:--"
        proxima_paciente = None

        if proxima:
            proxima_label = proxima.start_time.strftime("%H:%M")
            proxima_paciente = proxima.patient.full_name if proxima.patient else None

        proximas_rows = (
            db.query(Consultation)
            .filter(
                Consultation.user_id == user_id,
                Consultation.date >= today,
                Consultation.status != "Cancelada",
            )
            .order_by(Consultation.date, Consultation.start_time)
            .limit(5)
            .all()
        )

        # Extrai os campos ainda dentro da sessão — o relacionamento
        # `patient` é carregado sob demanda (lazy loading) e não pode
        # mais ser acessado depois que db.close() roda no `finally`.
        proximas = [
            {
                "id": item.id,
                "date": item.date,
                "start_time": item.start_time,
                "title": item.title,
                "status": item.status,
                "patient_name": item.patient.full_name if item.patient else "-",
            }
            for item in proximas_rows
        ]

        return {
            "consultas_hoje": consultas_hoje,
            "consultas_semana": consultas_semana,
            "total_pacientes": total_pacientes,
            "proxima_horario": proxima_label,
            "proxima_paciente": proxima_paciente,
            "proximas": proximas,
        }
    finally:
        db.close()
