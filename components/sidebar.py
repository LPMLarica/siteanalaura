from pathlib import Path
from streamlit_option_menu import option_menu
import streamlit as st


MENU = {
    "Dashboard": "dashboard",
    "Agenda": "consultas",
    "Pacientes": "pacientes",
    "Configurações": "configuracoes"
}

# Mapeamento inverso para descobrir qual item destacar no menu a partir
# da página atual (inclui páginas "internas", como o prontuário, que não
# aparecem como opção mas pertencem ao grupo "Pacientes").
PAGE_TO_LABEL = {
    "dashboard": "Dashboard",
    "consultas": "Agenda",
    "pacientes": "Pacientes",
    "prontuario": "Pacientes",
    "configuracoes": "Configurações"
}


def sidebar():

    with st.sidebar:

        st.markdown("<br>", unsafe_allow_html=True)

        logo_path = Path("assets/logo.png")

        if logo_path.exists():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(str(logo_path), width=90)
        else:
            st.markdown(
                "<div style='text-align:center;font-size:48px'>🌸</div>",
                unsafe_allow_html=True
            )

        st.markdown(
            """
            <h2 style="margin-bottom:0;text-align:center">
                Agenda Psicóloga
            </h2>

            <p style="color:#808080;text-align:center">
                Sistema Clínico
            </p>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        current_page = st.session_state.get("page", "dashboard")
        current_label = PAGE_TO_LABEL.get(current_page, "Dashboard")
        options = list(MENU.keys())
        default_index = (
            options.index(current_label)
            if current_label in options
            else 0
        )

        selected = option_menu(

            menu_title=None,

            options=options,

            icons=[
                "house",
                "calendar3",
                "people",
                "gear"
            ],

            default_index=default_index,

            styles={

                "container": {
                    "padding": "0",
                    "background-color": "#FFFDFE"
                },

                "icon": {
                    "color": "#D98CA8",
                    "font-size": "18px"
                },

                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "6px",
                    "border-radius": "12px",
                    "color": "#404040"
                },

                "nav-link-selected": {
                    "background-color": "#D98CA8",
                    "color": "white"
                }

            }

        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        # Quando o usuário está dentro do prontuário de um paciente,
        # oferece um caminho rápido de volta para a lista de pacientes.
        if current_page == "prontuario":
            if st.button("⬅ Voltar para Pacientes", use_container_width=True):
                st.session_state.page = "pacientes"
                st.session_state.pop("selected_patient", None)
                st.session_state.pop("patient_id", None)
                st.rerun()

        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        clicked_page = MENU[selected]

        # Só atualiza a página quando o usuário efetivamente troca de item
        # no menu — assim não sobrescreve navegações internas (como abrir
        # o prontuário de um paciente) feitas fora da sidebar.
        if selected != current_label:
            st.session_state.page = clicked_page

        return st.session_state.get("page", clicked_page)