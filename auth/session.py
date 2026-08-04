import streamlit as st


def initialize_session():

    defaults = {

        "authenticated": "",

        "user": "",

        "credentials": "",

        "page": "dashboard"

    }


    for key,value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value



def login_user(
        user,
        credentials
):

    st.session_state.authenticated = True

    st.session_state.user = user

    st.session_state.credentials = credentials



def logout():

    for key in list(
        st.session_state.keys()
    ):

        del st.session_state[key]


    st.rerun()



def current_user():

    return st.session_state.get(
        "user"
    )



def is_authenticated():

    return st.session_state.get(
        "authenticated"
    )