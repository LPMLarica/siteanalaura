import streamlit as st
from datetime import time
from dados.database import SessionLocal
from dados.models import WorkingHours



DAYS = {
    "Segunda":0,
    "Terça":1,
    "Quarta":2,
    "Quinta":3,
    "Sexta":4,
    "Sábado":5,
    "Domingo":6
}



def availability_form(user_id):

    st.subheader(
        "⏰ Horários de atendimento"
    )

    day = st.selectbox(
        "Dia",
        list(DAYS.keys())
    )

    inicio = st.time_input(
        "Início",
        time(8,0)
    )

    fim = st.time_input(
        "Fim",
        time(18,0)
    )

    if st.button("Salvar horário"):

        db = SessionLocal()

        item = WorkingHours(
            user_id=user_id,
            weekday=DAYS[day],
            start_time=inicio,
            end_time=fim
        )

        db.add(item)
        db.commit()
        db.close()

        st.success("Horário salvo")