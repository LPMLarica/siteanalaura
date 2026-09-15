import streamlit as st
from supabase import create_client, Client
import config
from config.settings import settings


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Client:
    """
    Cria (e reutiliza, via cache do Streamlit) o cliente do Supabase
    usado para autenticação de usuários (login/cadastro).

    O banco de dados relacional em si (pacientes, consultas, prontuários
    etc.) é acessado separadamente via SQLAlchemy, apontando para a
    connection string Postgres do mesmo projeto Supabase
    (settings.DATABASE_URL) — não pelo cliente REST aqui criado.
    """

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL/SUPABASE_KEY não configurados. Preencha essas "
            "variáveis no arquivo .env (veja .env.example) com os dados "
            "do seu projeto em https://app.supabase.com."
        )

    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )
