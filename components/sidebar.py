from streamlit_option_menu import option_menu
import streamlit as st


MENU = {
    "Dashboard": "dashboard",
    "Agenda": "consultas",
    "Pacientes": "pacientes",
    "Configurações": "configuracoes"
}


def sidebar():

    with st.sidebar:

        st.markdown("<br>", unsafe_allow_html=True)

        st.image(
            "assets/logo.png",
            width=90
        )

        st.markdown(
            """
            <h2 style="margin-bottom:0">
                Agenda Psicóloga
            </h2>

            <p style="color:#808080">
                Sistema Clínico
            </p>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        selected = option_menu(

            menu_title=None,

            options=[

                "Dashboard",

                "Agenda",

                "Pacientes",

                "Configurações"

            ],


            icons=[

                "house",

                "calendar3",

                "people",

                "gear"

            ],

            default_index=0,

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

        if st.button("⬅ Voltar"):

            pass

        if st.button("🚪 Sair"):

            st.session_state.clear()

            st.rerun()

        return MENU[selected]