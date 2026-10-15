from datetime import timedelta
from decimal import Decimal

from sqlalchemy import func, select

from dados.database import session_scope
from dados.models import Patient
from services.consultation_service import list_consultations
from services.payment_service import outstanding, received_between
from utils.formatting import add_months, first_day_of_month, today


def get_dashboard_stats(user_id):
    day = today()
    week_start = day - timedelta(days=day.weekday())
    week_end = week_start + timedelta(days=6)
    month_start = first_day_of_month(day)
    month_end = add_months(day, 1) - timedelta(days=1)

    active = ("Agendada", "Confirmada", "Realizada")

    today_items = [
        item for item in list_consultations(user_id, day, day)
        if item.status != "Cancelada"
    ]

    week_count = len(list_consultations(user_id, week_start, week_end, statuses=active))

    upcoming = list_consultations(
        user_id, day + timedelta(days=1), day + timedelta(days=14),
        statuses=("Agendada", "Confirmada"),
    )[:8]

    with session_scope() as db:
        active_patients = db.scalar(
            select(func.count()).select_from(Patient).where(
                Patient.user_id == user_id, Patient.status == "Ativo"
            )
        )

    pending = outstanding(user_id)

    return {
        "today": today_items,
        "week_count": week_count,
        "active_patients": active_patients or 0,
        "upcoming": upcoming,
        "received_month": received_between(user_id, month_start, month_end),
        "pending_total": sum((row["amount"] for row in pending), Decimal("0")),
        "pending": pending,
        "unconfirmed_tomorrow": [
            item for item in list_consultations(user_id, day + timedelta(days=1), day + timedelta(days=1))
            if item.status == "Agendada"
        ],
    }
