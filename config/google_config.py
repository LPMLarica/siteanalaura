import json
import os

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]


ENV_FILE = PROJECT_ROOT / ".env"


load_dotenv(
    dotenv_path=ENV_FILE
)


GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID"
)

GOOGLE_CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET"
)

GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI"
)


CREDENTIALS_FILE = (
    PROJECT_ROOT
    / "credentials"
    / "google_credentials.json"
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

    GOOGLE_REDIRECT_URI = (
        "http://localhost:8501"
    )


if GOOGLE_REDIRECT_URI:

    GOOGLE_REDIRECT_URI = GOOGLE_REDIRECT_URI.rstrip("/")