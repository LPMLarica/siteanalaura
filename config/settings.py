import os

from dotenv import load_dotenv


load_dotenv()


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

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-me"
    )

    GOOGLE_CLIENT_ID = os.getenv(
        "GOOGLE_CLIENT_ID"
    )

    GOOGLE_CLIENT_SECRET = os.getenv(
        "GOOGLE_CLIENT_SECRET"
    )

    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8501"
    )

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