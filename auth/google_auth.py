from google_auth_oauthlib.flow import Flow

from config.google_config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI
)


SCOPES = [

    "openid",

    "email",

    "profile",

    "https://www.googleapis.com/auth/calendar",

    "https://www.googleapis.com/auth/calendar.events"

]


def validate_configuration():

    if not GOOGLE_CLIENT_ID:

        raise RuntimeError(
            "GOOGLE_CLIENT_ID não configurado."
        )

    if not GOOGLE_CLIENT_SECRET:

        raise RuntimeError(
            "GOOGLE_CLIENT_SECRET não configurado."
        )

    if not GOOGLE_REDIRECT_URI:

        raise RuntimeError(
            "GOOGLE_REDIRECT_URI não configurado."
        )


def create_flow():

    validate_configuration()

    client_config = {

        "web": {

            "client_id":
                GOOGLE_CLIENT_ID,

            "client_secret":
                GOOGLE_CLIENT_SECRET,

            "auth_uri":
                "https://accounts.google.com/o/oauth2/auth",

            "token_uri":
                "https://oauth2.googleapis.com/token",

            "redirect_uris": [

                GOOGLE_REDIRECT_URI

            ]

        }

    }

    flow = Flow.from_client_config(

        client_config,

        scopes=SCOPES

    )

    flow.redirect_uri = (
        GOOGLE_REDIRECT_URI
    )

    return flow


def authorization_url():

    flow = create_flow()

    auth_url, state = (
        flow.authorization_url(

            access_type="offline",

            include_granted_scopes="true",

            prompt="consent"

        )
    )

    return auth_url, state


def exchange_code(
    code,
    state=None
):

    if not code:

        raise ValueError(
            "Código de autorização não fornecido."
        )

    flow = create_flow()

    if state:

        flow.state = state

    flow.fetch_token(
        code=code
    )

    return flow.credentials