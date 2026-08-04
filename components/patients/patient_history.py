import streamlit as st



def patient_history(consultations):

    st.subheader("📋 Histórico")

    if not consultations:
        st.info("Nenhuma consulta registrada.")

        return

    for item in consultations:
        with st.expander(f"{item.date} - {item.status}"):
            st.write(
                f"Horário: {item.start_time}"
            )

            st.write(
                f"Observação: {item.observation or '-'}"
            )