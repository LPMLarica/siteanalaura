import streamlit as st


def dashboard_card(
        title: str,
        value: str,
        emoji: str
):

    st.markdown(

        f"""

        <div class="dashboard-card">

            <h4>{emoji} {title}</h4>

            <h1>{value}</h1>

        </div>

        """,

        unsafe_allow_html=True

    )