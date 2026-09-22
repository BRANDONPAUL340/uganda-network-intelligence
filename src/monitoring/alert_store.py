import sys
from pathlib import Path

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sqlalchemy import text
from src.database import engine  # Reuses centralized core configuration engine pool [INDEX]
from src.monitoring.alerts import Alert


def get_open_alert(alert_name: str) -> dict | None:
    """
    Looks up the database audit ledger to determine if there is an active 
    incident with the same name currently marked as OPEN [INDEX].
    """
    query = text(
        """
        SELECT alert_id, alert_name, severity, message, triggered_at, resolved_at, status
        FROM alert_history
        WHERE alert_name = :alert_name AND status = 'OPEN'
        ORDER BY triggered_at DESC
        LIMIT 1;
        """
    )
    with engine.connect() as conn:
        row = conn.execute(query, {"alert_name": alert_name}).fetchone()
        return dict(row._mapping) if row else None


def save_alert(alert: Alert) -> dict:
    """
    Saves an alert into the database using a strict deduplication fence. 
    If the alert is already OPEN, it suppresses duplicate row generation [INDEX].
    """
    existing = get_open_alert(alert.name)
    if existing:
        return {
            "created": False,
            "alert_id": existing["alert_id"],
            "message": "Suppressed duplicate entry. Existing alert remains OPEN.",
        }

    query = text(
        """
        INSERT INTO alert_history (alert_name, severity, message, status)
        VALUES (:alert_name, :severity, :message, 'OPEN')
        RETURNING alert_id;
        """
    )
    with engine.begin() as conn:
        alert_id = conn.execute(
            query,
            {
                "alert_name": alert.name,
                "severity": alert.severity,
                "message": alert.message,
            },
        ).scalar()

        return {
            "created": True,
            "alert_id": alert_id,
            "message": "New operational alert state generated.",
        }


def resolve_alert(alert_name: str) -> bool:
    """
    Transitions an active incident from OPEN to RESOLVED, stamping the precise 
    timestamp when the operational path recovered [INDEX].
    """
    query = text(
        """
        UPDATE alert_history
        SET status = 'RESOLVED',
            resolved_at = CURRENT_TIMESTAMP
        WHERE alert_name = :alert_name AND status = 'OPEN';
        """
    )
    with engine.begin() as conn:
        result = conn.execute(query, {"alert_name": alert_name})
        return result.rowcount > 0
