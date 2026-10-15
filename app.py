import logging

import streamlit as st

from components.ui import LOGO, inject_css
from config.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon=str(LOGO) if LOGO.exists() else "🌸",
    layout="wide",
    initial_sidebar_state="auto",
)

inject_css()


# --------------------------------------------------- configuração e banco


def _setup_problem(title, items):
    st.markdown(f"## {title}")

    for item in items:
        st.markdown(f"- {item}")

    if any(item.startswith("SECRET_KEY") for item in items):
        from cryptography.fernet import Fernet

        st.markdown(
            "Sugestão de **SECRET_KEY** gerada agora (copie e guarde uma cópia em "
            "local seguro — ela não pode ser trocada depois que houver prontuários):"
        )
        st.code(Fernet.generate_key().decode(), language=None)

    st.info(
        "No Streamlit Community Cloud, preencha em **Settings → Secrets** do app. "
        "Localmente, use `.streamlit/secrets.toml` ou `.env`. O README explica cada valor."
    )
    st.stop()


problems = settings.problems()

if problems:
    _setup_problem("Configuração incompleta", problems)


@st.cache_resource(show_spinner="Conectando ao banco de dados...")
def _prepare_database():
    from dados.database import check_connection, init_db

    error = check_connection()

    if error:
        return error

    init_db()
    return None


db_error = _prepare_database()

def _db_hints(error):
    text = (error or "").lower()

    if "password authentication failed" in text:
        return [
            "A **senha do banco** foi recusada pelo Supabase.",
            "Redefina em Supabase → Project Settings → Database → **Reset database password** "
            "e copie a senha nova.",
            "Coloque a senha no secret **DATABASE_PASSWORD** (assim caracteres especiais "
            "como @ # / % não quebram a URL). Na DATABASE_URL a senha pode ficar como "
            "`[YOUR-PASSWORD]`.",
        ]

    if "could not translate host name" in text or "network is unreachable" in text or "cannot assign requested address" in text:
        return [
            "O endereço do banco não foi alcançado. No Streamlit Cloud use a URI do "
            "**Session pooler** (host `aws-...pooler.supabase.com`), não a conexão direta "
            "`db.<projeto>.supabase.co`.",
        ]

    if "tenant or user not found" in text:
        return [
            "O pooler não reconheceu o usuário. No Session pooler o usuário é "
            "`postgres.kzwwtywsvwhywlbzyidd` (com o código do projeto), não só `postgres`.",
        ]

    return [
        "Confira a DATABASE_URL (use a URI do *Session pooler* do Supabase) e a senha.",
        "Se o projeto do Supabase estiver pausado, reative-o no painel (Restore project).",
    ]


if db_error:
    _prepare_database.clear()
    logging.error("Falha ao conectar ao banco: %s", db_error)
    _setup_problem("Não foi possível conectar ao banco de dados", _db_hints(db_error))


# ------------------------------------------------------------ autenticação

from auth.session import is_authenticated  # noqa: E402
from components.sidebar import sidebar_brand, sidebar_footer  # noqa: E402
from views.agenda import agenda  # noqa: E402
from views.configuracoes import configuracoes  # noqa: E402
from views.dashboard import dashboard  # noqa: E402
from views.financeiro import financeiro  # noqa: E402
from views.login import login_page  # noqa: E402
from views.pacientes import pacientes  # noqa: E402

sidebar_brand()

if not is_authenticated():
    login_page()
    st.stop()


# --------------------------------------------------------------- navegação

pages = {
    "dashboard": st.Page(dashboard, title="Início", icon=":material/home:", url_path="inicio", default=True),
    "agenda": st.Page(agenda, title="Agenda", icon=":material/calendar_month:", url_path="agenda"),
    "pacientes": st.Page(pacientes, title="Pacientes", icon=":material/groups:", url_path="pacientes"),
    "financeiro": st.Page(financeiro, title="Financeiro", icon=":material/payments:", url_path="financeiro"),
    "configuracoes": st.Page(configuracoes, title="Configurações", icon=":material/settings:", url_path="configuracoes"),
}

st.session_state["pages"] = pages

navigation = st.navigation(list(pages.values()))

sidebar_footer()

flash = st.session_state.pop("flash", None)

if flash:
    message, icon = flash
    st.toast(message, icon=icon)

try:
    navigation.run()
except Exception:  # pragma: no cover - rede de segurança da interface
    logging.exception("Erro não tratado na página")
    st.error(
        "Algo deu errado ao carregar esta tela. Tente novamente; se continuar, "
        "recarregue a página."
    )
