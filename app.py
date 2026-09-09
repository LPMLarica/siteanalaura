import streamlit as st
from pathlib import Path
from config.settings import settings
from auth.session import (
    initialize_session,
    is_authenticated
)
from pages.login import login_page
from components.sidebar import sidebar
from pages.dashboard import dashboard
from pages.consultas import consultas
#from dotenv import load_dotenv

#load_dotenv()


if not st.user.is_logged_in:
    if st.button("Log in"):
        st.login()
else:
    if st.button("Log out"):
        st.logout()
    st.write(f"Hello, {st.user.name}!")
