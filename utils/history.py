import streamlit as st


def initialize_history():

    if "history" not in st.session_state:

        st.session_state.history = []


def push(page):

    initialize_history()

    history = st.session_state.history

    if len(history) == 0:

        history.append(page)

        return

    if history[-1] != page:

        history.append(page)


def back():

    initialize_history()

    history = st.session_state.history

    if len(history) > 1:

        history.pop()

        return history[-1]

    return "dashboard"