import streamlit as st
from auth.session import current_user
from components.forms.availability_form import (
    availability_form
)



def configuracoes():

    user=current_user()

    st.title(
        "⚙ Configurações"
    )

    tab1,tab2 = st.tabs(
        [
        "Horários",
        "Conta"
        ]
    )

    with tab1:
        availability_form(
            user["id"]
        )

    with tab2:
        st.write(
            user
        )