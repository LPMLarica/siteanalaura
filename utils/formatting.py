"""Datas no fuso da clínica, formatação brasileira e validações."""

import re
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from config.settings import settings

MONTHS = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]

WEEKDAYS_SHORT = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
WEEKDAYS_LONG = [
    "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
    "sexta-feira", "sábado", "domingo",
]


# ------------------------------------------------------------------ tempo


def tz():
    return ZoneInfo(settings.TIMEZONE)


def now_local():
    """Agora, no fuso da clínica (o servidor do Streamlit roda em UTC)."""
    return datetime.now(tz())


def today():
    return now_local().date()


def to_local(dt):
    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.astimezone(tz())


# ------------------------------------------------------------- formatação


def fmt_date(value, with_weekday=False):
    if not value:
        return "-"

    text = value.strftime("%d/%m/%Y")

    if with_weekday:
        text = f"{WEEKDAYS_SHORT[value.weekday()]}, {text}"

    return text


def fmt_date_long(value):
    return f"{WEEKDAYS_LONG[value.weekday()]}, {value.day} de {MONTHS[value.month - 1]}"


def fmt_time(value):
    return value.strftime("%H:%M") if value else "--:--"


def fmt_datetime(value):
    value = to_local(value)
    return value.strftime("%d/%m/%Y %H:%M") if value else "-"


def fmt_money(value):
    value = Decimal(value or 0)
    text = f"{value:,.2f}"
    return "R$ " + text.replace(",", "X").replace(".", ",").replace("X", ".")


def month_label(year, month):
    return f"{MONTHS[month - 1].capitalize()} de {year}"


def age(birth_date, reference=None):
    if not birth_date:
        return None

    reference = reference or today()

    return reference.year - birth_date.year - (
        (reference.month, reference.day) < (birth_date.month, birth_date.day)
    )


def to_decimal(value):
    if value in (None, ""):
        return None

    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def combine(day, moment):
    return datetime.combine(day, moment if isinstance(moment, time) else time())


# -------------------------------------------------------------- validação


def only_digits(value):
    return re.sub(r"\D", "", value or "")


def format_cpf(value):
    digits = only_digits(value)

    if len(digits) != 11:
        return value

    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def is_valid_cpf(value):
    digits = only_digits(value)

    if len(digits) != 11 or digits == digits[0] * 11:
        return False

    for size in (9, 10):
        total = sum(int(digits[i]) * (size + 1 - i) for i in range(size))
        check = (total * 10) % 11 % 10

        if check != int(digits[size]):
            return False

    return True


def format_phone(value):
    digits = only_digits(value)

    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"

    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"

    return value


def is_valid_email(value):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", (value or "").strip()))


def whatsapp_link(phone, message=""):
    digits = only_digits(phone)

    if len(digits) in (10, 11):
        digits = "55" + digits

    if len(digits) < 12:
        return None

    from urllib.parse import quote

    return f"https://wa.me/{digits}" + (f"?text={quote(message)}" if message else "")


def first_day_of_month(day):
    return date(day.year, day.month, 1)


def add_months(day, months):
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)
