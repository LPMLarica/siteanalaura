import streamlit as st


def patient_card(patient):

    with st.container():

        st.markdown(

        f"""

        <div style="

        background:white;

        padding:20px;

        border-radius:18px;

        box-shadow:

        0 8px 20px rgba(0,0,0,.05);

        ">


        <h3>

        👩 {patient.full_name}

        </h3>


        <p>

        📞 {patient.phone or '-'}

        </p>


        <p>

        Status:

        {patient.status}

        </p>


        </div>

        """,

        unsafe_allow_html=True

        )