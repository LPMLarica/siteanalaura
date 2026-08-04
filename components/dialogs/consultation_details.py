import streamlit as st


from services.consultation_service import (
    update_consultation,
    delete_consultation
)




def consultation_details(
        consultation
):


    st.subheader(
        "Detalhes da Consulta"
    )


    st.write(

        f"Paciente: {consultation.patient.full_name}"

    )


    st.write(

        f"Data: {consultation.date}"

    )


    st.write(

        f"Horário: {consultation.start_time}"

    )


    st.write(

        f"Observação: {consultation.observation}"

    )


    status = st.selectbox(

        "Status",

        [

            "Agendada",

            "Confirmada",

            "Cancelada",

            "Remarcada"

        ],

        index=[

            "Agendada",

            "Confirmada",

            "Cancelada",

            "Remarcada"

        ].index(

            consultation.status

        )

    )



    col1,col2 = st.columns(2)



    with col1:


        if st.button(
            "Salvar"
        ):


            update_consultation(

                consultation.id,

                {

                "status":
                status

                }

            )


            st.success(
                "Atualizado"
            )


            st.rerun()



    with col2:


        if st.button(
            "Excluir"
        ):


            delete_consultation(

                consultation.id

            )


            st.warning(
                "Removido"
            )


            st.rerun()