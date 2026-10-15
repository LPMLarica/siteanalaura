import json
from datetime import datetime, timedelta

import streamlit as st
from streamlit_calendar import calendar

from auth.session import current_user
from components.consultation_dialogs import consultation_dialog, new_consultation_dialog
from components.ui import empty_state, page_header, payment_badge, slot_row, status_badge, status_legend
from dados.models import STATUS_COLORS
from services.consultation_service import calendar_events, list_consultations, reschedule_consultation
from services.schedule_service import ScheduleError, blocked_periods_between, list_working_hours
from utils.formatting import fmt_date_long, fmt_time, now_local

CALENDAR_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Source+Sans+3:wght@400;600&display=swap');
.fc { font-family: 'Source Sans 3', 'Source Sans Pro', sans-serif; }
.fc .fc-toolbar-title { font-family: 'Fraunces', Georgia, serif; font-size: 1.35rem; color: #2F2A2C; text-transform: none !important; }
.fc .fc-button-primary { background: #FFFFFF; color: #7A3F57; border-color: #E8DFE2; text-transform: capitalize; }
.fc .fc-button-primary:hover { background: #F4ECEE; color: #7A3F57; border-color: #E8DFE2; }
.fc .fc-button-primary:not(:disabled).fc-button-active,
.fc .fc-button-primary:not(:disabled):active { background: #975670; border-color: #975670; color: #FFFFFF; }
.fc .fc-button-primary:disabled { background: #F4ECEE; color: #A08D95; border-color: #E8DFE2; }
.fc-theme-standard td, .fc-theme-standard th, .fc-theme-standard .fc-scrollgrid { border-color: #EFE7EA; }
.fc .fc-day-today { background: #FBF3F5 !important; }
.fc .fc-col-header-cell-cushion { color: #6F6670; text-transform: capitalize; font-weight: 600; }
.fc .fc-daygrid-day-number { color: #6F6670; }
.fc-event { border-radius: 6px; padding: 1px 3px; font-size: 0.82rem; cursor: pointer; }
.fc .fc-bg-event { background: #E3D7DC; opacity: 0.55; }
.fc .fc-timegrid-now-indicator-line { border-color: #975670; }
"""


def _parse(value):
    """ISO vindo do calendário (em UTC "de parede") -> datetime sem fuso."""
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def _remember_view(view):
    if not view:
        return
    st.session_state["calendar_view"] = view.get("type") or "timeGridWeek"
    start = _parse(view.get("currentStart"))
    if start:
        st.session_state["calendar_date"] = start.date().isoformat()


def _bump():
    st.session_state["calendar_version"] = st.session_state.get("calendar_version", 0) + 1


def _business_hours(user_id):
    hours = list_working_hours(user_id)

    return [
        {
            # FullCalendar: 0 = domingo; no app: 0 = segunda.
            "daysOfWeek": [(item.weekday + 1) % 7],
            "startTime": item.start_time.strftime("%H:%M"),
            "endTime": item.end_time.strftime("%H:%M"),
        }
        for item in hours
        if item.active
    ]


def _calendar_tab(user):
    today = now_local().date()

    # Janela de eventos generosa ao redor da data em exibição.
    focus = st.session_state.get("calendar_date") or today.isoformat()
    focus_date = datetime.fromisoformat(focus).date()
    window_start = focus_date - timedelta(days=45)
    window_end = focus_date + timedelta(days=75)

    hide_cancelled = st.session_state.get("hide_cancelled", True)

    events = calendar_events(user["id"], window_start, window_end, hide_cancelled=hide_cancelled)

    for block in blocked_periods_between(user["id"], window_start, window_end):
        events.append(
            {
                "id": f"block-{block.id}",
                "title": block.reason or "Agenda bloqueada",
                "start": block.start_date.isoformat(),
                "end": (block.end_date + timedelta(days=1)).isoformat(),
                "display": "background",
                "allDay": True,
            }
        )

    business = _business_hours(user["id"])

    options = {
        "locale": "pt-br",
        # O calendário trabalha em "UTC" para exibir exatamente o horário
        # gravado, independentemente do fuso do navegador.
        "timeZone": "UTC",
        "now": now_local().strftime("%Y-%m-%dT%H:%M:%S"),
        "initialView": st.session_state.get("calendar_view", "timeGridWeek"),
        "initialDate": focus,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
        },
        "buttonText": {"today": "hoje", "month": "mês", "week": "semana", "day": "dia", "list": "lista"},
        "firstDay": 1,
        "allDaySlot": False,
        "slotMinTime": "07:00:00",
        "slotMaxTime": "22:00:00",
        "slotDuration": "00:30:00",
        "scrollTime": "08:00:00",
        "nowIndicator": True,
        "editable": True,
        "eventDurationEditable": True,
        "selectable": True,
        "selectMirror": True,
        "dayMaxEvents": 3,
        "height": 720,
        "eventTimeFormat": {"hour": "2-digit", "minute": "2-digit", "hour12": False},
        "slotLabelFormat": {"hour": "2-digit", "minute": "2-digit", "hour12": False},
        "noEventsText": "Nenhuma consulta neste período",
    }

    if business:
        options["businessHours"] = business

    version = st.session_state.get("calendar_version", 0)

    state = calendar(
        events=events,
        options=options,
        custom_css=CALENDAR_CSS,
        callbacks=["dateClick", "eventClick", "eventChange", "select"],
        key=f"agenda_{version}",
    )

    st.toggle("Ocultar canceladas", key="hide_cancelled", value=True)

    if not state or "callback" not in state:
        return

    # O componente devolve o último evento a cada recarga; guardamos uma
    # assinatura para tratar cada interação uma única vez.
    signature = f"{version}:" + json.dumps(state, sort_keys=True, default=str)

    if st.session_state.get("calendar_last") == signature:
        return

    st.session_state["calendar_last"] = signature
    callback = state["callback"]
    payload = state.get(callback) or {}

    if callback == "eventClick":
        _remember_view(payload.get("view"))
        event_id = str((payload.get("event") or {}).get("id") or "")

        if event_id.isdigit():
            _bump()
            consultation_dialog(int(event_id))

    elif callback in ("dateClick", "select"):
        _remember_view(payload.get("view"))
        start = _parse(payload.get("date") or payload.get("start"))
        end = _parse(payload.get("end"))
        all_day = payload.get("allDay", False)
        duration = None

        if end and not all_day:
            minutes = int((end - start).total_seconds() // 60)
            duration = minutes if 30 < minutes <= 240 else None

        _bump()
        new_consultation_dialog(
            day=start.date(),
            start=None if all_day else start.time(),
            duration=duration,
        )

    elif callback == "eventChange":
        event = payload.get("event") or {}
        event_id = str(event.get("id") or "")
        start = _parse(event.get("start"))
        end = _parse(event.get("end"))

        if not event_id.isdigit() or not start:
            return

        if not end:
            old = payload.get("oldEvent") or {}
            old_start, old_end = _parse(old.get("start")), _parse(old.get("end"))
            end = start + ((old_end - old_start) if old_start and old_end else timedelta(minutes=50))

        st.session_state["calendar_date"] = start.date().isoformat()

        try:
            reschedule_consultation(
                int(event_id), user["id"], start.date(), start.time(), end.time(), force=True
            )
        except ScheduleError as error:
            st.session_state["flash"] = (f"Não foi possível mover: {error}", "⚠️")
        else:
            st.session_state["flash"] = (
                f"Consulta movida para {start:%d/%m} às {start:%H:%M}.", "✅"
            )

        _bump()
        st.rerun()


def _list_tab(user):
    today = now_local().date()

    c1, c2 = st.columns([1, 1])
    start = c1.date_input("De", value=today, format="DD/MM/YYYY", key="agenda_list_from")
    end = c2.date_input("Até", value=today + timedelta(days=6), format="DD/MM/YYYY", key="agenda_list_to")

    if end < start:
        st.warning("A data final precisa ser depois da inicial.")
        return

    items = list_consultations(user["id"], start, end)

    if not items:
        empty_state("Nenhuma consulta neste período.")
        return

    current_day = None

    for item in items:
        if item.date != current_day:
            current_day = item.date
            st.markdown(f'<div class="day-title">{fmt_date_long(item.date)}</div>', unsafe_allow_html=True)

        paid = bool(item.payment and item.payment.status == "Pago")
        right_html = status_badge(item.status)

        if item.status in ("Realizada", "Falta"):
            right_html += " " + payment_badge(paid)

        cols = st.columns([12, 2], vertical_alignment="center")

        with cols[0]:
            slot_row(
                fmt_time(item.start_time),
                fmt_time(item.end_time),
                item.patient.full_name,
                f"{item.title} · {item.modality}",
                right_html,
                tone=STATUS_COLORS.get(item.status),
            )

        if cols[1].button("Abrir", key=f"open_{item.id}", width="stretch"):
            consultation_dialog(item.id)


def agenda():
    user = current_user()

    head, action = st.columns([4, 1], vertical_alignment="bottom")

    with head:
        page_header("Agenda", "Clique em um horário para agendar; arraste uma consulta para remarcar.", eyebrow="Consultas")

    if action.button("Nova consulta", type="primary", width="stretch"):
        new_consultation_dialog()

    status_legend()

    view = st.segmented_control(
        "Visualização",
        ["Calendário", "Lista"],
        default="Calendário",
        key="agenda_mode",
        label_visibility="collapsed",
    )

    if view == "Lista":
        _list_tab(user)
    else:
        _calendar_tab(user)
