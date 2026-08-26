from textwrap import dedent

import streamlit as st

from auth.google_auth import authorization_url
from auth.google_auth import exchange_code

from auth.auth_service import decode_google_user

from auth.session import login_user

from services.user_service import get_or_create_user
from config.google_config import GOOGLE_REDIRECT_URI


def login_page():

    # ==========================================================
    # CSS
    # ==========================================================

    st.markdown(
        dedent(
            """
        <style>
        .stApp:has([class*="st-key-login-card"]) {
            background:
                radial-gradient(circle at 15% 15%, rgba(231, 190, 198, .32), transparent 32%),
                radial-gradient(circle at 85% 85%, rgba(191, 211, 198, .32), transparent 28%),
                #f7f3f1;
        }

        .stApp:has([class*="st-key-login-card"]) section[data-testid="stSidebar"] {
            display: none;
        }

        .stApp:has([class*="st-key-login-card"]) .block-container {
            max-width: 100%;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        [class*="st-key-login-card"] {
            box-sizing: border-box;
            width: min(100%, 440px);
            margin: 5vh auto 0;
            padding: clamp(2rem, 6vw, 3.25rem);
            border: 1px solid rgba(117, 91, 94, .12);
            border-radius: 20px;
            background: rgba(255, 255, 255, .94);
            box-shadow: 0 20px 55px rgba(86, 63, 65, .14);
        }

        [class*="st-key-login-card"] .login-card-content {
            text-align: center;
        }

        .login-mark {
            width: 52px;
            height: 52px;
            display: grid;
            place-items: center;
            margin: 0 auto 1.35rem;
            border-radius: 50%;
            background: #9b5f70;
            color: #fff;
            font-size: 18px;
            font-weight: 700;
            letter-spacing: .04em;
        }

        .login-title {
            margin: 0 0 .65rem;
            color: #342b2d;
            font-family: Georgia, serif;
            font-size: clamp(25px, 5vw, 31px);
            font-weight: 600;
            line-height: 1.15;
        }

        .login-subtitle {
            max-width: 285px;
            margin: 0 auto;
            color: #75696b;
            font-size: 14px;
            line-height: 1.65;
        }

        .login-divider {
            width: 42px;
            height: 2px;
            margin: 1.6rem auto 0;
            background: #d9a7b1;
        }

        [class*="st-key-login-card"] .stLinkButton {
            display: block;
            width: 100%;
            margin-top: 1.8rem;
        }

        [class*="st-key-login-card"] .stLinkButton a {
            box-sizing: border-box;
            width: 100%;
            padding: 13px 18px;
            border: 1px solid #d7c5c6;
            border-radius: 10px;
            background: #fff;
            color: #4a3d40 !important;
            text-decoration: none !important;
            font-size: 14px;
            font-weight: 600;
            text-align: center;
            transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
        }

        [class*="st-key-login-card"] .stLinkButton a:hover {
            border-color: #9b5f70;
            box-shadow: 0 8px 18px rgba(155, 95, 112, .14);
            transform: translateY(-1px);
        }

        .login-error {
            margin-top: 1.8rem;
            padding: 11px 13px;
            border: 1px solid #e5bfc4;
            border-radius: 10px;
            background: #fff5f5;
            color: #8c454f;
            font-size: 13px;
            line-height: 1.45;
        }

        .login-footer {
            margin-top: 1.45rem;
            color: #9a8d8f;
            font-size: 11px;
            line-height: 1.5;
        }

        @media (max-width: 480px) {
            [class*="st-key-login-card"] {
                margin-top: 1rem;
                border-radius: 16px;
            }
        }

        </style>
        """,
        ),
        unsafe_allow_html=True
    )


    # ==========================================================
    # Espaçamento
    # ==========================================================

    st.markdown(
        "",
        unsafe_allow_html=True
    )


    # ==========================================================
    # Verificar callback do Google
    # ==========================================================

    query_params = st.query_params

    pending_error = st.session_state.pop(
        "login_error",
        None
    )

    if pending_error:

        render_login_card(
            None,
            pending_error["message"],
            pending_error["details"]
        )

        return

    if "error" in query_params:

        error = query_params.get(
            "error"
        )

        st.error(
            f"Não foi possível realizar o login Google: {error}"
        )

        if st.button(
            "Tentar novamente",
            use_container_width=True
        ):

            st.query_params.clear()

            st.rerun()


        return


    if "code" in query_params:

        process_google_callback(
            query_params["code"]
        )

        return


    # ==========================================================
    # Criar URL OAuth
    # ==========================================================

    try:

        auth_url, state = authorization_url()

        st.session_state["oauth_state"] = state

    except RuntimeError as error:

        render_login_card(
            None,
            str(error)
        )

        return

    except Exception as error:

        render_login_card(
            None,
            "Erro ao preparar o login Google."
        )

        st.exception(error)

        return


    # ==========================================================
    # Interface
    # ==========================================================

    render_login_card(
        auth_url
    )


# ==============================================================
# CARD
# ==============================================================


def render_login_card(
    auth_url=None,
    error=None,
    error_details=None
):

    with st.container(key="login-card", border=False):
        st.markdown(
            dedent(
                """
            <div class="login-card-content">
                <div class="login-mark">A</div>
                <div class="login-title">Agenda Psicóloga</div>
                <div class="login-subtitle">
                    Organize seus atendimentos<br>
                    de forma simples e elegante.
                </div>
                <div class="login-divider"></div>
            </div>
            """,
            ),
            unsafe_allow_html=True
        )

        if error:
            st.error(error)

            if error_details:
                with st.expander("Detalhes técnicos"):
                    st.code(error_details)

        elif auth_url:
            st.link_button("G  Entrar com Google", auth_url, use_container_width=True)

        st.markdown(
            dedent(
                """
            <div class="login-footer">
                Acesso seguro utilizando autenticação do Google.
            </div>
            """,
            ),
            unsafe_allow_html=True
        )


# ==============================================================
# CALLBACK GOOGLE
# ==============================================================


def process_google_callback(code):

    try:

        oauth_state = st.session_state.get(
            "oauth_state"
        )

        credentials = exchange_code(
            code,
            state=oauth_state
        )


        google_user = decode_google_user(
            credentials
        )


        user = get_or_create_user(
            google_user
        )


        if not user.active:

            st.error(
                "Este usuário está desativado."
            )

            st.query_params.clear()

            return


        login_user(

            {

                "id": user.id,

                "name": user.name,

                "email": user.email,

                "picture": user.picture

            },

            credentials

        )


        # Limpa ?code=...
        st.query_params.clear()


        st.success(
            "Login realizado com sucesso!"
        )


        st.rerun()


    except Exception as error:

        error_text = str(error)
        error_lower = error_text.lower()
        is_redirect_error = "redirect_uri_mismatch" in error_lower
        is_expired_code = (
            "invalid_grant" in error_lower
            or "invalid authorization code" in error_lower
        )
        is_state_error = "state" in error_lower and "mismatch" in error_lower

        if is_redirect_error:
            error_message = (
                "O Google recusou o retorno do login porque o endereço de "
                "redirecionamento não está cadastrado exatamente nas credenciais OAuth."
            )
            error_details = (
                f"Cadastre este URI no Google Cloud: {GOOGLE_REDIRECT_URI}\n\n"
                f"Erro original: {error_text}"
            )
        elif is_expired_code:
            error_message = "A sessão de login expirou. Inicie o login novamente."
            error_details = error_text
        elif is_state_error:
            error_message = "A sessão de login expirou. Inicie o login novamente."
            error_details = error_text
        else:
            error_message = (
                "Não foi possível concluir o login. Verifique a configuração "
                "do Google e tente novamente."
            )
            error_details = error_text or error.__class__.__name__

        st.session_state["login_error"] = {
            "message": error_message,
            "details": error_details
        }
        st.query_params.clear()
        st.rerun()