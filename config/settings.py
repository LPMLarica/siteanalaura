import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    # Valores com fallback sensato: o app sobe mesmo sem .env completo.
    # Apenas as credenciais do Google são obrigatórias para usar login/agenda.
    APP_NAME = os.getenv("APP_NAME", "Agenda Psicóloga")

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///storage/app.db")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

    CLIENT_SECRET_ID = os.getenv("GOOGLE_CLIENT_SECRET")

    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")

    TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")

    @property
    def google_configured(self) -> bool:
        return bool(self.CLIENT_ID and self.CLIENT_SECRET_ID)


settings = Settings()