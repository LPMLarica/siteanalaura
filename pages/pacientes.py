import streamlit as st
from auth.session import current_user
from services.patient_service import (
    get_patients
)
from components.patients.patient_form import (
    patient_form
)
from components.patients.patient_card import (
    patient_card
)
from components.patients.patient_profile import (
    patient_profile
)


def pacientes():

    user=current_user()

    st.title("👩 Pacientes")

    aba1,aba2 = st.tabs(
        [
        "Lista",
        "Novo Paciente"
        ]
    )


    with aba1:

        patients = get_patients(
            user["id"]
        )

        if not patients:
            st.info("Nenhum paciente cadastrado")

        for patient in patients:
            if st.button(
                f"👩 {patient.full_name}",
                use_container_width=True
            ):
                st.session_state.selected_patient = patient.id

            if "selected_patient" in st.session_state:

                from services.patient_service import get_patient

                patient = get_patient(
                    
                    st.session_state.selected_patient
                    
                )

                patient_profile(

                    patient
                    
                )

    with aba2:
        patient_form(
            user["id"]
        )