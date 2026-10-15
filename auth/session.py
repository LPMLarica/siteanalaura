"""Estado de login guardado na sessão do Streamlit (por aba do navegador)."""

import time

import streamlit as st

from config.settings import settings


def login_user(user):
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.last_activity = time.time()


def logout():
    st.session_state.clear()


def current_user():
    return st.session_state.get("user")


def is_authenticated():
    if not st.session_state.get("authenticated"):
        return False

    timeout = settings.SESSION_TIMEOUT_MINUTES * 60
    last = st.session_state.get("last_activity", 0)

    if timeout and time.time() - last > timeout:
        logout()
        st.session_state.session_expired = True
        return False

    st.session_state.last_activity = time.time()

    return True


def update_current_user(**fields):
    user = dict(st.session_state.get("user") or {})
    user.update(fields)
    st.session_state.user = user
