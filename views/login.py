import logging

import streamlit as st

from auth.session import login_user
from auth.supabase_auth import (
    AuthError,
    reset_password_with_code,
    send_password_reset,
    sign_in,
    sign_up,
    validate_new_password,
)
from components.ui import LOGO
from config.settings import settings
from services.audit_service import register_action
from services.user_service import get_or_create_user

logger = logging.getLogger(__name__)


def login_page():
    left, center, right = st.columns([1, 2.2, 1])

    with center:
        with st.container(key="login-card"):
            if LOGO.exists():
                a, b, c = st.columns([1, 1, 1])
                b.image(str(LOGO), width="stretch")

            st.markdown(
                f'<div class="login-title">{settings.APP_NAME}</div>'
                '<div class="login-sub">Agenda, pacientes e prontuário em um só lugar.</div>',
                unsafe_allow_html=True,
            )

            if st.session_state.pop("session_expired", False):
                st.info("Sua sessão expirou por inatividade. Entre novamente.")

            labels = ["Entrar"]

            if settings.ALLOW_SIGNUP:
                labels.append("Criar conta")

            labels.append("Esqueci a senha")

            tabs = st.tabs(labels)

            with tabs[0]:
                _login_form()

            index = 1

            if settings.ALLOW_SIGNUP:
                with tabs[index]:
                    _signup_form()
                index += 1

            with tabs[index]:
                _recovery_form()

            st.markdown(
                '<div class="login-foot">Acesso protegido. Os registros clínicos '
                "são criptografados antes de serem gravados.</div>",
                unsafe_allow_html=True,
            )


def _login_form():
    with st.form("login_form", border=False):
        email = st.text_input("E-mail", autocomplete="email")
        password = st.text_input("Senha", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("Entrar", type="primary", width="stretch")

    if not submitted:
        return

    try:
        with st.spinner("Entrando..."):
            account = sign_in(email, password)
            user = get_or_create_user(account)
    except AuthError as error:
        st.error(str(error))
        return
    except Exception:
        logger.exception("Falha inesperada no login")
        st.error("Não foi possível entrar agora. Verifique a conexão e tente novamente.")
        return

    if not user["active"]:
        st.error("Sua conta está desativada.")
        return

    login_user(user)
    register_action(user["id"], "Entrou no sistema")
    st.rerun()


def _signup_form():
    with st.form("signup_form", border=False):
        name = st.text_input("Nome completo")
        email = st.text_input("E-mail", key="signup_email", autocomplete="email")
        password = st.text_input("Senha", type="password", key="signup_pw", autocomplete="new-password",
                                 help="Mínimo de 8 caracteres, com letras e números.")
        confirmation = st.text_input("Confirmar senha", type="password", key="signup_pw2", autocomplete="new-password")
        submitted = st.form_submit_button("Criar conta", type="primary", width="stretch")

    if not submitted:
        return

    if not name.strip() or not email.strip():
        st.error("Preencha nome e e-mail.")
        return

    problem = validate_new_password(password, confirmation)

    if problem:
        st.error(problem)
        return

    try:
        with st.spinner("Criando conta..."):
            account, needs_confirmation = sign_up(email, password, " ".join(name.split()))
            get_or_create_user(account)
    except AuthError as error:
        st.error(str(error))
        return
    except Exception:
        logger.exception("Falha inesperada no cadastro")
        st.error("Não foi possível criar a conta agora. Tente novamente.")
        return

    if needs_confirmation:
        st.success(
            "Conta criada! Enviamos um link de confirmação para o seu e-mail. "
            "Depois de confirmar, entre pela aba \"Entrar\"."
        )
    else:
        st.success("Conta criada! Agora é só entrar pela aba \"Entrar\".")


def _recovery_form():
    st.caption("Enviaremos um código de verificação para o e-mail cadastrado.")

    with st.form("recovery_request", border=False):
        email = st.text_input("E-mail da conta", key="recovery_email")
        send = st.form_submit_button("Enviar código", width="stretch")

    if send:
        try:
            send_password_reset(email)
        except AuthError as error:
            st.error(str(error))
        else:
            st.session_state["recovery_sent_to"] = email.strip().lower()
            st.success("Se o e-mail estiver cadastrado, o código chegará em instantes.")

    sent_to = st.session_state.get("recovery_sent_to")

    if not sent_to:
        return

    with st.form("recovery_confirm", border=False):
        code = st.text_input("Código recebido", max_chars=10)
        password = st.text_input("Nova senha", type="password", key="recovery_pw", autocomplete="new-password")
        confirmation = st.text_input("Confirmar nova senha", type="password", key="recovery_pw2", autocomplete="new-password")
        reset = st.form_submit_button("Redefinir senha", type="primary", width="stretch")

    if reset:
        problem = validate_new_password(password, confirmation)

        if problem:
            st.error(problem)
            return

        try:
            reset_password_with_code(sent_to, code, password)
        except AuthError as error:
            st.error(str(error))
        else:
            st.session_state.pop("recovery_sent_to", None)
            st.success("Senha redefinida! Entre com a nova senha na aba \"Entrar\".")
