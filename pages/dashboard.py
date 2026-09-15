import streamlit as st

from auth.session import current_user
from components.cards import dashboard_card
from services.dashboard_service import get_dashboard_stats


def dashboard():

    st.title("🌸 Dashboard")

    user = current_user()

    stats = get_dashboard_stats(user["id"])

    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        dashboard_card(
            "Consultas Hoje",
            str(stats["consultas_hoje"]),
            "🗓️"
        )

    with c2:
        dashboard_card(
            "Consultas Semana",
            str(stats["consultas_semana"]),
            "🌷"
        )

    with c3:
        dashboard_card(
            "Pacientes",
            str(stats["total_pacientes"]),
            "👩"
        )

    with c4:
        dashboard_card(
            "Próxima Consulta",
            stats["proxima_horario"],
            "💗"
        )

    st.write("")
    st.write("")

    st.subheader("📅 Próximas consultas")

    if not stats["proximas"]:
        st.info("Nenhuma consulta agendada. Vá até \"Agenda\" para marcar uma.")
    else:
        for item in stats["proximas"]:
            st.markdown(
                f"""
                <div class="dashboard-card" style="margin-bottom:8px;">
                    <b>{item['date'].strftime('%d/%m/%Y')} às {item['start_time'].strftime('%H:%M')}</b>
                    — {item['patient_name']} · {item['title']}
                    <span style="color:#808080;"> ({item['status']})</span>
                </div>
                """,
                unsafe_allow_html=True
            )
