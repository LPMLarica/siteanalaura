import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    APP_NAME = os.getenv("APP_NAME")

    DATABASE_URL = os.getenv("DATABASE_URL")

    SECRET_KEY = os.getenv("SECRET_KEY")

    CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

    CLIENT_SECRET_ID = os.getenv("GOOGLE_CLIENT_SECRET")

    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

    TIMEZONE = os.getenv("TIMEZONE")


settings = Settings()