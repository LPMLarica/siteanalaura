import streamlit as st


def consultas():

    st.title("Consultas")

    st.markdown("---")

    aba1, aba2, aba3 = st.tabs(

        [

            "Marcar",

            "Remarcar",

            "Cancelar"

        ]

    )

    with aba1:

        st.text_input(

            "Nome do paciente"

        )

        st.date_input(

            "Data"

        )

        st.time_input(

            "Horário"

        )

        st.text_area(

            "Observação"

        )

        st.button(

            "Salvar Consulta"

        )

    with aba2:

        st.info(

            "Será implementado."

        )

    with aba3:

        st.info(

            "Será implementado."

        )