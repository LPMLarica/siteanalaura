import json
import os

from pathlib import Path
from turtle import st

from dotenv import load_dotenv


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]


#ENV_FILE = PROJECT_ROOT / ".env"


#load_dotenv(
    #dotenv_path=ENV_FILE
#)


GOOGLE_CLIENT_ID = st.secrets["client_id"]

SECRET_KEY = st.secrets["cookie_secret"]

GOOGLE_CLIENT_SECRET = st.secrets["client_secret"]

GOOGLE_REDIRECT_URI = st.secrets["redirect_uri"]


CREDENTIALS_FILE = (
    PROJECT_ROOT
    / ".streamlit"
    / "secrets.toml"
    #/ "credentials"
    #/ "google_credentials.json"
)


def _clean(value):

    if not value:
        return None

    if not isinstance(value, str):
        return value

    if "${" in value:
        return None

    return value.strip()


if (
    not GOOGLE_CLIENT_ID
    or not GOOGLE_CLIENT_SECRET
):

    if CREDENTIALS_FILE.exists():

        try:

            data = json.loads(
                CREDENTIALS_FILE.read_text(
                    encoding="utf-8"
                )
            )

            web = data.get(
                "web",
                {}
            )

            GOOGLE_CLIENT_ID = (
                GOOGLE_CLIENT_ID
                or _clean(
                    web.get("client_id")
                )
            )

            SECRET_KEY = (
                SECRET_KEY
                or _clean(
                    web.get("client_secret")
                )
            )

            GOOGLE_CLIENT_SECRET = (
                GOOGLE_CLIENT_SECRET
                or _clean(
                    web.get("client_secret")
                )
            )

            if not GOOGLE_REDIRECT_URI:

                redirect_uris = (
                    web.get(
                        "redirect_uris",
                        []
                    )
                )

                if redirect_uris:

                    GOOGLE_REDIRECT_URI = _clean(
                        redirect_uris[0]
                    )

        except (
            OSError,
            json.JSONDecodeError
        ):

            pass


if not GOOGLE_REDIRECT_URI:

    GOOGLE_REDIRECT_URI = ( st.secrets.get("redirect_uri") )


if GOOGLE_REDIRECT_URI:

    GOOGLE_REDIRECT_URI = GOOGLE_REDIRECT_URI.rstrip("/")