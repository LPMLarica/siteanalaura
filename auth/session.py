import streamlit as st


def initialize_session():

    defaults = {

        "authenticated": False,

        "user": None,

        "credentials": None,

        "page": "dashboard",

        "history": []

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


def login_user(
    user,
    credentials
):

    st.session_state.authenticated = True

    st.session_state.user = user

    st.session_state.credentials = credentials

    st.session_state.page = "dashboard"

    if "history" not in st.session_state:

        st.session_state.history = []

    st.session_state.history = [
        "dashboard"
    ]


def logout():

    keys_to_remove = [

        "authenticated",

        "user",

        "credentials",

        "page",

        "history"

    ]

    for key in keys_to_remove:

        st.session_state.pop(
            key,
            None
        )

    st.rerun()


def current_user():

    return st.session_state.get(
        "user"
    )


def current_credentials():

    return st.session_state.get(
        "credentials"
    )


def is_authenticated():

    return bool(
        st.session_state.get(
            "authenticated",
            False
        )
    )