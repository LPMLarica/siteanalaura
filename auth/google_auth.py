import json

from pathlib import Path


from google_auth_oauthlib.flow import Flow


from config.config import (
    CREDENTIALS_DIR
)



SCOPES = [

    "openid",

    "https://www.googleapis.com/auth/userinfo.email",

    "https://www.googleapis.com/auth/userinfo.profile",

    "https://www.googleapis.com/auth/calendar"

]



def create_flow():


    credentials = (

        Path(
            CREDENTIALS_DIR
        )

        /
        "google_credentials.json"

    )


    flow = Flow.from_client_secrets_file(

        credentials,

        scopes=SCOPES,

        redirect_uri=
        "http://localhost:8501"

    )


    return flow



def authorization_url():

    flow = create_flow()


    url,state = (

        flow.authorization_url(

            access_type="offline",

            include_granted_scopes=True

        )

    )


    return url



def exchange_code(code):

    flow=create_flow()


    flow.fetch_token(

        code=code

    )


    return flow.credentials