import streamlit as st
from auth.session import current_user
from components.calendar.calendar import (
    render_calendar
)
from components.forms.consultation_form import (
    consultation_form
)
from services.calendar_service import (
    get_calendar_events
)
from services.consultation_service import (
    get_consultation
)
from components.calendar.handlers import (
    handle_calendar_events
)
from components.dialogs.consultation_details import (
    consultation_details
)


def consultas():


    st.title("🌸 Agenda")
    user = current_user()
    aba1, aba2 = st.tabs(

        [
            "📅 Calendário",
            "➕ Nova Consulta"
        ]
    )

    with aba1:

        events = get_calendar_events(user["id"])

        calendar_state = render_calendar(events)

        handle_calendar_events(
            calendar_state,
            user["id"]
        )

        # Quando o usuário clica em um evento (em vez de arrastar/
        # redimensionar), render_calendar devolve o payload do
        # "eventClick" diretamente — identificado pela chave "event".
        if calendar_state and "event" in calendar_state:

            event_id = int(calendar_state["event"]["id"])

            consultation = get_consultation(
                event_id,
                user["id"]
            )

            if consultation:
                st.divider()
                consultation_details(
                    consultation,
                    user["id"]
                )

    with aba2:

        consultation_form(
            user["id"]
        )