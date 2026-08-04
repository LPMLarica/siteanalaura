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
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(

    page_title=settings.APP_NAME,

    page_icon="🌸",

    layout="wide",

    initial_sidebar_state="expanded"

)



css = Path(
    "assets/css/main.css"
)


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

