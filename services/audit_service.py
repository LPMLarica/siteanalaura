import logging

from sqlalchemy import select

from dados.database import session_scope
from dados.models import AuditLog

logger = logging.getLogger(__name__)


def register_action(user_id, action, target=None):
    """Registra uma ação sensível. Nunca derruba a tela se falhar."""

    try:
        with session_scope() as db:
            db.add(
                AuditLog(
                    user_id=user_id,
                    action=action[:255],
                    target=(target or "")[:255] or None,
                )
            )
    except Exception:
        logger.exception("Falha ao registrar auditoria")


def recent_actions(user_id, limit=50):
    with session_scope() as db:
        return db.scalars(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        ).all()
