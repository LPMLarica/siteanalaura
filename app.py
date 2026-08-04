import streamlit as st

from config.settings import settings

from pathlib import Path


st.set_page_config(

    page_title=settings.APP_NAME,

    page_icon="🧠",

    layout="wide",

    initial_sidebar_state="expanded"

)


css = Path("assets/style.css")

if css.exists():

    st.markdown(

        f"<style>{css.read_text(encoding='utf8')}</style>",

        unsafe_allow_html=True

    )


if "logged" not in st.session_state:

    st.session_state.logged = False


st.title("🧠 Agenda da Psicóloga")


st.info(

    "Projeto inicial carregado com sucesso."

)


st.success(

    "Estrutura criada."

)