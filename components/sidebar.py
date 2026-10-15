from html import escape

import streamlit as st

from auth.session import current_user, logout
from components.ui import LOGO
from config.settings import settings


def sidebar_brand():
    """Logo e nome no topo da barra lateral (acima do menu de páginas)."""

    if LOGO.exists():
        st.logo(str(LOGO), size="large")


def sidebar_footer():
    user = current_user() or {}

    with st.sidebar:
        st.markdown(
            '<div class="brand">'
            f'<div class="brand-name">{escape(settings.PROFESSIONAL_NAME)}</div>'
            '<div class="brand-sub">Psicologia</div></div>',
            unsafe_allow_html=True,
        )

        st.divider()

        register = user.get("professional_register")
        st.markdown(
            f'<div class="who"><b>{escape(user.get("name") or "")}</b>'
            + (f"<br>CRP {escape(register)}" if register else "")
            + f'<br>{escape(user.get("email") or "")}</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button("Sair", width="stretch", icon=":material/logout:"):
            logout()
            st.rerun()
