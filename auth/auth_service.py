from google.oauth2 import id_token

from google.auth.transport import requests



def decode_google_user(
        credentials
):


    user = id_token.verify_oauth2_token(

        credentials.id_token,

        requests.Request()

    )


    return {


        "google_id":
            user["sub"],


        "name":
            user.get("name"),


        "email":
            user.get("email"),


        "picture":
            user.get("picture")

    }