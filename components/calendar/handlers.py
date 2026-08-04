import streamlit as st


from services.calendar_event_service import (
    process_calendar_update
)



def handle_calendar_events(state,user_id):

    if not state:
        return

    if "eventChange" in state:

        try:
            process_calendar_update(
                state["eventChange"],
                user_id
            )

            st.success("Consulta atualizada")

            st.rerun()

        except Exception as error:

            st.error(
                str(error)
            )