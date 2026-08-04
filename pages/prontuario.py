import streamlit as st
from auth.session import current_user
from services.patient_service import get_patient
from services.clinical_record_service import (
    get_patient_records
)
from components.records.record_form import (
    record_form
)
from components.records.record_history import (
    record_history
)
from services.audit_service import register_action

def prontuario(patient_id):

    user = current_user()

    patient = get_patient(
        patient_id
    )

    register_action(
        user["id"],
        "Visualizou prontuário",
        patient.full_name
    )
    

    st.title(f"📖 Prontuário - {patient.full_name}")

    tab1,tab2 = st.tabs(
        [
            "Novo registro",
            "Histórico"
        ]
    )

    with tab1:
        record_form(
            patient.id,
            user["id"]
        )

    with tab2:
        records = get_patient_records(
            patient.id
        )

        record_history(
            records
        )