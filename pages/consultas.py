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
from components.calendar.handlers import (
    handle_calendar_events
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

        render_calendar(
            events
        )



    with aba2:

        consultation_form(
            user["id"],
            st.session_state.credentials
        )