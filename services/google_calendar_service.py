from googleapiclient.discovery import build

from datetime import datetime



TIMEZONE = "America/Sao_Paulo"


def get_calendar_service(credentials):

    return build(
        "calendar",
        "v3",
        credentials=credentials
    )


def create_google_event(credentials,consultation):

    service = get_calendar_service(credentials)

    event = {

        "summary":
            f"{consultation.title} - {consultation.patient.full_name}",
        "description":
            consultation.observation or "",

        "start": {
            "dateTime":
            datetime.combine(
                consultation.date,
                consultation.start_time
            ).isoformat(),
            "timeZone":TIMEZONE
        },

        "end": {
            "dateTime": 
            datetime.combine(
                consultation.date,
                consultation.end_time
            ).isoformat(),
            "timeZone":TIMEZONE
        },

        "colorId":"6"

    }

    result = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return result["id"]


def update_google_event(credentials,event_id,consultation):

    service = get_calendar_service(credentials)

    event = {

        "summary":f"{consultation.title} - {consultation.patient.full_name}",

        "start": {
            "dateTime":
            datetime.combine(
                consultation.date,
                consultation.start_time
            ).isoformat(),
            "timeZone":TIMEZONE
        },



        "end": {
            "dateTime":
            datetime.combine(
                consultation.date,
                consultation.end_time
            ).isoformat(),
            "timeZone":TIMEZONE
        }
    }

    service.events().update(
        calendarId="primary",
        eventId=event_id,
        body=event
    ).execute()


def delete_google_event(credentials,event_id):

    service = get_calendar_service(credentials)

    service.events().delete(
        calendarId="primary",
        eventId=event_id
    ).execute()