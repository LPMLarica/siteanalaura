import streamlit as st

from services.patient_service import (
    create_patient
)



def patient_form(user_id):

    st.subheader("👩 Novo Paciente")

    name = st.text_input("Nome completo")

    cpf = st.text_input("CPF")

    birth = st.date_input("Data nascimento")

    phone = st.text_input("Telefone")

    email = st.text_input("Email")

    address = st.text_input("Endereço")

    notes = st.text_area("Observações")

    if st.button("Cadastrar",use_container_width=True):

        if not name:
            st.error("Informe o nome")

            return

        create_patient(

            {

                "user_id":user_id,
                "full_name":name,
                "cpf":cpf,
                "birth_date":birth,
                "phone":phone,
                "email":email,
                "address":address,
                "notes":notes

            }
        )

        st.success("Paciente cadastrado!")

        st.rerun()