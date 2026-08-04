import streamlit as st

from streamlit_calendar import calendar



def render_calendar(events):


    options = {

            "editable": True,

            "selectable": True,

            "initialView":"dayGridMonth",

            "locale":"pt-br",

            "headerToolbar": {

                "left": "prev,next today",

                "center": "title",

                "right": "dayGridMonth,timeGridWeek,timeGridDay"
            }
        }
    
    state = calendar(
        events,
        options=options,
        key="agenda"
    )

    if state:

        if "eventClick" in state:
            return state["eventClick"]

    return state
