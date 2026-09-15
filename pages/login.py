import logging
import os

import streamlit as st

from auth.session import login_user
from auth.supabase_auth import sign_in, sign_up
from services.user_service import get_or_create_user

logger = logging.getLogger(__name__)


def login_page():

    with st.container(key="login-card", border=False):

        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            logo_path = "assets/logo.png"
            if os.path.exists(logo_path):
                st.image(logo_path, width=140)

        st.markdown(
            """
            <h1 style="text-align:center;margin-bottom:0;">
                Agenda Psicóloga Ana Laura
            </h1>
            <p style="text-align:center;color:#808080;">
                Organize seus atendimentos de forma simples e elegante.
            </p>
            """,
            unsafe_allow_html=True
        )

        tab_login, tab_signup = st.tabs(
            [
                "Entrar",
                "Criar conta"
            ]
        )

        with tab_login:
            _render_login_form()

        with tab_signup:
            _render_signup_form()

        st.markdown(
            """
            <p style="text-align:center;color:#B0B0B0;font-size:13px;margin-top:24px;">
                Acesso seguro — seus dados ficam protegidos com login por
                senha e criptografia dos registros clínicos.
            </p>
            """,
            unsafe_allow_html=True
        )


def _render_login_form():

    with st.form("login_form"):

        email = st.text_input(
            "E-mail",
            key="login_email"
        )

        password = st.text_input(
            "Senha",
            type="password",
            key="login_password"
        )

        submitted = st.form_submit_button(
            "Entrar",
            use_container_width=True
        )

    if not submitted:
        return

    if not email or not password:
        st.error("Informe e-mail e senha.")
        return

    try:
        supabase_user = sign_in(
            email.strip(),
            password
        )

        user = get_or_create_user(supabase_user)

        if not user.active:
            st.error(
                "Sua conta está desativada. Fale com o administrador do sistema."
            )
            return

        login_user(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email
            },
            None
        )

        st.rerun()

    except Exception as error:
        # Mensagens do Supabase (ex.: "Invalid login credentials",
        # "Email not confirmed") já são adequadas para o usuário final —
        # só evitamos expor stack traces de outros erros inesperados.
        logger.exception("Falha no login")
        st.error(_friendly_message(error, "Não foi possível entrar."))


def _render_signup_form():

    with st.form("signup_form"):

        name = st.text_input(
            "Nome completo",
            key="signup_name"
        )

        email = st.text_input(
            "E-mail",
            key="signup_email"
        )

        password = st.text_input(
            "Senha",
            type="password",
            key="signup_password"
        )

        password_confirm = st.text_input(
            "Confirmar senha",
            type="password",
            key="signup_password_confirm"
        )

        submitted = st.form_submit_button(
            "Criar conta",
            use_container_width=True
        )

    if not submitted:
        return

    if not name or not email or not password:
        st.error("Preencha todos os campos.")
        return

    if password != password_confirm:
        st.error("As senhas não coincidem.")
        return

    if len(password) < 6:
        st.error("A senha deve ter pelo menos 6 caracteres.")
        return

    try:
        supabase_user = sign_up(
            email.strip(),
            password,
            name.strip()
        )

        get_or_create_user(supabase_user)

        st.success(
            "Conta criada! Se a confirmação por e-mail estiver ativada "
            "no seu projeto Supabase, verifique sua caixa de entrada "
            "antes de entrar pela aba \"Entrar\"."
        )

    except Exception as error:
        logger.exception("Falha no cadastro")
        st.error(_friendly_message(error, "Não foi possível criar a conta."))


def _friendly_message(error, fallback):
    """
    O cliente do Supabase normalmente já levanta mensagens adequadas
    para exibir ao usuário (ex.: "User already registered"). Para
    qualquer outro erro inesperado (rede, configuração ausente etc.),
    cai no texto genérico em `fallback` em vez de vazar detalhes
    internos na tela de login.
    """

    text = str(error).strip()

    if text and len(text) < 200:
        return text

    return fallback
