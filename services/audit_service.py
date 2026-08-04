from database.database import SessionLocal
from database.models import AuditLog


def register_action(user_id,action,target):

    db = SessionLocal()

    log = AuditLog(
        user_id=user_id,
        action=action,
        target=target
    )

    db.add(log)
    db.commit()
    db.close()