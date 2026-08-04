import streamlit as st
from datetime import datetime, timedelta
from services.patient_service import (
    get_patients
)
from services.consultation_service import (
    create_consultation
)



COLORS = {

    "Consulta inicial":
    "#D98CA8",

    "Retorno":
    "#DCCDF7",

    "Confirmada":
    "#A8D5BA",

    "Urgência":
    "#F4C2C2"

}



def consultation_form(user_id, credentials):

    st.subheader("🌸 Nova Consulta")

    patients = get_patients(user_id)

    if not patients:
        st.warning("Cadastre pacientes primeiro.")
        
        return

    patient_options = {
        p.full_name:
        p.id
        for p in patients
    }

    patient_name = st.selectbox(
        "Paciente",
        list(
            patient_options.keys()
        )
    )

    date = st.date_input(
        "Data"
    )

    start_time = st.time_input(
        "Horário inicial",
        value=datetime.now().time()
    )

    duration = st.selectbox(
        "Duração",
        [
            30,45,50,60,90
        ],
        index=2
    )

    start_datetime = datetime.combine(date,start_time)

    end_time = (start_datetime+timedelta(minutes=duration)).time()

    title = st.text_input(
        "Título",
        "Consulta"
    )

    status = st.selectbox(
        "Status",

        [
            "Agendada",
            "Confirmada",
            "Cancelada"
        ]
    )

    color_name = st.selectbox(
        "Categoria",
        list(COLORS.keys())
    )

    observation = st.text_area("Observações")

    if st.button("Salvar Consulta",use_container_width=True):

        data = {
            "patient_id": patient_options[patient_name],
            "user_id":user_id,
            "date":date,
            "start_time":start_time,
            "end_time":end_time,
            "title":title,
            "status":status,
            "color":COLORS[color_name],
            "observation":observation
        }

        create_consultation(
            data,
            credentials
        )

        st.success("Consulta criada!")

        st.rerun()