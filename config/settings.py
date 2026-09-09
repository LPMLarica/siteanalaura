import os
import streamlit as st

#from dotenv import load_dotenv


#load_dotenv()


class Settings:

    APP_NAME = os.getenv(
        "APP_NAME",
        "Agenda Psicóloga"
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///storage/app.db"
    )

    DATABASE_BACKEND = os.getenv(
        "DATABASE_BACKEND",
        "sqlite"
    )

    FIREBASE_CREDENTIALS = (
        os.getenv("FIREBASE_CREDENTIALS")
        or os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
    )

    SECRET_KEY = st.secrets["cookie_secret"]

    GOOGLE_CLIENT_ID = st.secrets["client_id"]

    GOOGLE_CLIENT_SECRET = st.secrets["client_secret"]

    GOOGLE_REDIRECT_URI = st.secrets["redirect_uri"]

    TIMEZONE = os.getenv(
        "TIMEZONE",
        "America/Sao_Paulo"
    )

    @property
    def google_configured(self):

        return bool(
            self.GOOGLE_CLIENT_ID
            and self.GOOGLE_CLIENT_SECRET
        )


settings = Settings()