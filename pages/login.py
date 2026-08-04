import streamlit as st

from auth.google_auth import authorization_url

from auth.google_auth import exchange_code

from auth.auth_service import decode_google_user

from auth.session import login_user

from services.user_service import get_or_create_user



def login_page():


    st.markdown(
        """
        <style>

        .login-card{

            background:white;

            width:420px;

            padding:40px;

            border-radius:24px;

            box-shadow:
            0px 15px 40px rgba(0,0,0,.08);

            margin:auto;

            text-align:center;

        }


        .login-title{

            color:#404040;

            font-size:28px;

            font-weight:600;

        }


        .login-subtitle{

            color:#808080;

            font-size:15px;

        }

        </style>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        "<br><br>",
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="login-card">

        <div class="login-title">
        🌸 Agenda Psicóloga
        </div>

        <br>

        <div class="login-subtitle">

        Organize seus atendimentos
        de forma simples e elegante.

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.write("")


    col1,col2,col3 = st.columns(
        [1,2,1]
    )


    with col2:


        if st.button(
            "🔐 Entrar com Google",
            use_container_width=True
        ):

            url = authorization_url()


            st.markdown(

                f"""

                <meta http-equiv="refresh"

                content="0; url={url}">

                """,

                unsafe_allow_html=True

            )



    query_params = st.query_params


    if "code" in query_params:


        code = query_params["code"]


        credentials = exchange_code(
            code
        )


        google_user = decode_google_user(
            credentials
        )


        user = get_or_create_user(
            google_user
        )


        login_user(

            {

                "id": user.id,

                "name": user.name,

                "email": user.email,

                "picture": user.picture

            },

            credentials

        )


        st.query_params.clear()


        st.rerun()