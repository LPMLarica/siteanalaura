"""Horários de atendimento, bloqueios (férias, feriados) e conflitos."""

from datetime import date, time

from sqlalchemy import select

from dados.database import session_scope
from dados.models import BlockedPeriod, Consultation, WorkingHours, WEEKDAYS


class ScheduleError(Exception):
    """Horário inválido; ``soft`` indica que a profissional pode forçar."""

    def __init__(self, message, soft=False):
        super().__init__(message)
        self.soft = soft


# ----------------------------------------------------- horários de trabalho


def list_working_hours(user_id):
    with session_scope() as db:
        return db.scalars(
            select(WorkingHours)
            .where(WorkingHours.user_id == user_id)
            .order_by(WorkingHours.weekday, WorkingHours.start_time)
        ).all()


def add_working_hours(user_id, weekdays, start_time, end_time):
    if end_time <= start_time:
        raise ScheduleError("O horário final precisa ser depois do inicial.")

    with session_scope() as db:
        existing = db.scalars(
            select(WorkingHours).where(
                WorkingHours.user_id == user_id,
                WorkingHours.weekday.in_(weekdays),
                WorkingHours.active.is_(True),
            )
        ).all()

        for item in existing:
            if start_time < item.end_time and end_time > item.start_time:
                raise ScheduleError(
                    f"Já existe um horário em {WEEKDAYS[item.weekday]} que se sobrepõe "
                    f"({item.start_time:%H:%M}–{item.end_time:%H:%M})."
                )

        for weekday in weekdays:
            db.add(
                WorkingHours(
                    user_id=user_id,
                    weekday=weekday,
                    start_time=start_time,
                    end_time=end_time,
                    active=True,
                )
            )


def delete_working_hours(item_id, user_id):
    with session_scope() as db:
        item = db.scalar(
            select(WorkingHours).where(WorkingHours.id == item_id, WorkingHours.user_id == user_id)
        )

        if item:
            db.delete(item)


# ----------------------------------------------------------------- bloqueios


def list_blocked_periods(user_id, from_date=None):
    with session_scope() as db:
        query = select(BlockedPeriod).where(BlockedPeriod.user_id == user_id)

        if from_date:
            query = query.where(BlockedPeriod.end_date >= from_date)

        return db.scalars(query.order_by(BlockedPeriod.start_date)).all()


def add_blocked_period(user_id, start_date, end_date, reason=None):
    if end_date < start_date:
        raise ScheduleError("A data final precisa ser igual ou depois da inicial.")

    with session_scope() as db:
        db.add(
            BlockedPeriod(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                reason=(reason or "").strip() or None,
            )
        )


def delete_blocked_period(item_id, user_id):
    with session_scope() as db:
        item = db.scalar(
            select(BlockedPeriod).where(BlockedPeriod.id == item_id, BlockedPeriod.user_id == user_id)
        )

        if item:
            db.delete(item)


def blocked_periods_between(user_id, start: date, end: date):
    with session_scope() as db:
        return db.scalars(
            select(BlockedPeriod).where(
                BlockedPeriod.user_id == user_id,
                BlockedPeriod.start_date <= end,
                BlockedPeriod.end_date >= start,
            )
        ).all()


# ---------------------------------------------------------------- validação


def validate_slot(db, user_id, day: date, start: time, end: time, ignore_id=None, force=False):
    """
    Levanta ScheduleError se o horário não puder ser usado.

    - fim antes do início, bloqueio e conflito com outra consulta: sempre
      impedem;
    - fora do horário de atendimento: aviso que pode ser ignorado
      (``force=True``). Se nenhum horário foi cadastrado, não há restrição.
    """

    if end <= start:
        raise ScheduleError("O horário final precisa ser depois do inicial.")

    blocked = db.scalar(
        select(BlockedPeriod).where(
            BlockedPeriod.user_id == user_id,
            BlockedPeriod.start_date <= day,
            BlockedPeriod.end_date >= day,
        )
    )

    if blocked:
        reason = f" ({blocked.reason})" if blocked.reason else ""
        raise ScheduleError(f"A agenda está bloqueada em {day:%d/%m/%Y}{reason}.")

    query = select(Consultation).where(
        Consultation.user_id == user_id,
        Consultation.date == day,
        Consultation.status != "Cancelada",
        Consultation.start_time < end,
        Consultation.end_time > start,
    )

    if ignore_id:
        query = query.where(Consultation.id != ignore_id)

    clash = db.scalar(query.limit(1))

    if clash:
        raise ScheduleError(
            f"Conflito com outra consulta em {day:%d/%m/%Y} "
            f"das {clash.start_time:%H:%M} às {clash.end_time:%H:%M}."
        )

    if force:
        return

    hours = db.scalars(
        select(WorkingHours).where(
            WorkingHours.user_id == user_id, WorkingHours.active.is_(True)
        )
    ).all()

    if not hours:
        return

    for item in hours:
        if item.weekday == day.weekday() and start >= item.start_time and end <= item.end_time:
            return

    raise ScheduleError(
        f"{day:%d/%m/%Y} às {start:%H:%M} está fora do seu horário de atendimento.",
        soft=True,
    )
