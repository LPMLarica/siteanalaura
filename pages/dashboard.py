import streamlit as st

from components.cards import dashboard_card


def dashboard():

    st.title("🌸 Dashboard")

    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        dashboard_card(
            "Consultas Hoje",
            "0",
            "🗓️"
        )

    with c2:
        dashboard_card(
            "Consultas Semana",
            "0",
            "🌷"
        )

    with c3:
        dashboard_card(
            "Pacientes",
            "0",
            "👩"
        )

    with c4:
        dashboard_card(
            "Próxima Consulta",
            "--:--",
            "💗"
        )

    st.write("")
    st.write("")

    st.markdown(
        """
        <div class="dashboard-card">

        <h3>📅 Calendário</h3>

        <br>

        O calendário profissional será integrado
        nas próximas etapas utilizando FullCalendar.

        </div>
        """,
        unsafe_allow_html=True
    )