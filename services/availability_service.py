from datetime import datetime
from dados.database import SessionLocal
from dados.models import (
    WorkingHours,
    BlockedSchedule,
    Consultation
)


def is_blocked(user_id,date):

    db = SessionLocal()

    blocked = (
        db.query(
            BlockedSchedule
        )

        .filter(
            BlockedSchedule.user_id == user_id,
            BlockedSchedule.date == date
        )

        .first()
    )

    db.close()

    return blocked is not None

def check_working_hours(user_id,date,start_time,end_time):

    weekday = date.weekday()

    db = SessionLocal()

    config = (
        db.query(
            WorkingHours
        )

        .filter(
            WorkingHours.user_id == user_id,
            WorkingHours.weekday == weekday,
            WorkingHours.active == True
        )

        .first()
    )

    db.close()

    if not config:
        return False

    return (
        start_time >= config.start_time
        and
        end_time <= config.end_time
    )


def available_slot(user_id,date,start_time,end_time):

    if is_blocked(
        user_id,
        date
    ):
        return False

    if not check_working_hours(
        user_id,
        date,
        start_time,
        end_time
    ):
        return False

    return True