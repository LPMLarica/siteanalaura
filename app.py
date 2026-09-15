import streamlit as st
from pathlib import Path

from config.settings import settings
from dados.database import init_db
from auth.session import (
    initialize_session,
    is_authenticated
)
from pages.login import login_page
from components.sidebar import sidebar
from pages.dashboard import dashboard
from pages.consultas import consultas
from pages.pacientes import pacientes
from pages.prontuario import prontuario
from pages.configuracoes import configuracoes


st.set_page_config(

    page_title=settings.APP_NAME,

    page_icon="🌸",

    layout="wide",

    initial_sidebar_state="expanded"

)


# Garante que as tabelas existam (Postgres do Supabase em produção,
# SQLite local em desenvolvimento) antes de qualquer consulta. Idempotente
# — não recria tabelas já existentes.
init_db()


css = Path(__file__).resolve().parent / "assets" / "css" / "main.css"


if css.exists():

    st.markdown(

        f"""

        <style>

        {css.read_text()}

        </style>

        """,

        unsafe_allow_html=True

    )


initialize_session()


if not is_authenticated():

    login_page()

    st.stop()


page = sidebar()


if page == "dashboard":

    dashboard()


elif page == "consultas":

    consultas()


elif page == "pacientes":

    pacientes()


elif page == "prontuario":

    patient_id = st.session_state.get("patient_id")

    if not patient_id:
        st.session_state.page = "pacientes"
        st.rerun()

    prontuario(patient_id)


elif page == "configuracoes":

    configuracoes()
