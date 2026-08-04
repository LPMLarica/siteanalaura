from google_auth_oauthlib.flow import Flow

import os


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



def create_flow():


    client_config = {


        "web":

        {

        "client_id":GOOGLE_CLIENT_ID,
        "client_secret":GOOGLE_CLIENT_SECRET,
        "response_type": "code",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://oauth2.googleapis.com/token",
        "redirect_uris":
        [
            GOOGLE_REDIRECT_URI
        ]

        }

    }



    flow = Flow.from_client_config(

        client_config,

        scopes=SCOPES

    )


    flow.redirect_uri = GOOGLE_REDIRECT_URI


    return flow


def authorization_url():
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        raise RuntimeError(
            "Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment or fill credentials/google_credentials.json."
        )

    flow = create_flow()
    auth_url =flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return auth_url


def exchange_code(code: str):
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        raise RuntimeError(
            "Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment or fill credentials/google_credentials.json."
        )

    flow = create_flow()
    # The Flow object needs the redirect_uri to match the one used in the auth request
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    # Exchange authorization code for credentials
    flow.fetch_token(code=code)
    return flow.credentials