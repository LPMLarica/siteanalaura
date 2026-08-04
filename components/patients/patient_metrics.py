import streamlit as st


def patient_metrics(total,next_consultation):

    col1,col2 = st.columns(2)

    with col1:

        st.metric(
            "Consultas realizadas",
            total
        )



    with col2:

        if next_consultation:

            value = (
                f"{next_consultation.date}"
                "\n"
                f"{next_consultation.start_time}"
            )

        else:
            value = "-"

        st.metric(
            "Próxima consulta",
            value
        )