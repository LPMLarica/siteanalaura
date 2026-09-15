import streamlit as st


from services.patient_history_service import (

    get_patient_consultations,

    count_patient_consultations,

    get_next_consultation

)


from components.patients.patient_metrics import (

    patient_metrics

)


from components.patients.patient_history import (

    patient_history

)

from services.payment_service import (

    get_patient_payment_summary

)



def patient_profile(patient, user_id):

    st.title(f"👩 {patient.full_name}")

    st.divider()

    col1,col2 = st.columns(2)



    with col1:

        st.write(
            f"📞 Telefone: {patient.phone or '-'}"
        )

        st.write(
            f"✉ Email: {patient.email or '-'}"
        )


    with col2:

        st.write(
            f"CPF: {patient.cpf or '-'}"
        )

        st.write(
            f"Status: {patient.status}"
        )


    st.divider()

    total = count_patient_consultations(
        patient.id
    )

    next_consultation = get_next_consultation(
        patient.id
    )

    patient_metrics(total,next_consultation)

    st.divider()

    st.subheader("💰 Pagamentos")

    summary = get_patient_payment_summary(
        patient.id,
        user_id
    )

    col_pago, col_pendente, col_qtd = st.columns(3)

    with col_pago:
        st.metric("Total pago", f"R$ {summary['total_pago']:.2f}")

    with col_pendente:
        st.metric("Total pendente", f"R$ {summary['total_pendente']:.2f}")

    with col_qtd:
        st.metric("Pagamentos registrados", summary["quantidade"])

    st.divider()

    st.subheader("📝 Observações")


    st.write(
        patient.notes or
        "Nenhuma observação."
    )

    st.divider()

    consultations = get_patient_consultations(
        patient.id
    )

    patient_history(
        consultations
    )

    if st.button("📖 Abrir Prontuário"):
        st.session_state.page = "prontuario"
        st.session_state.patient_id = patient.id
        st.rerun()