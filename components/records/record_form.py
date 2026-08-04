import streamlit as st
from services.clinical_record_service import (
    create_record
)


def record_form(patient_id,user_id):

    st.subheader(
        "📝 Nova evolução"
    )

    content = st.text_area(
        "Registro da sessão",
        height=200
    )


    if st.button(
        "Salvar evolução",
        use_container_width=True
        ):

        if not content:
            st.warning(
                "Digite uma observação."
            )

            return



        create_record(
            {
                "patient_id":patient_id,
                "user_id":user_id,
                "content":content
            }
        )

        st.success(
            "Registro salvo."
        )


        st.rerun()