from datetime import datetime

from services.consultation_service import (
    reschedule_consultation
)



def process_calendar_update(event_data,user_id):

    event_id = int(
        event_data["id"]
    )


    start = datetime.fromisoformat(
        event_data["start"]
    )


    end = datetime.fromisoformat(
        event_data["end"]
    )


    result = reschedule_consultation(
        consultation_id=event_id,
        user_id=user_id,
        new_date=start.date(),
        new_start=start.time(),
        new_end=end.time()
    )

    return result