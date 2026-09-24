import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sqlalchemy import text
from src.database import engine
from src.monitoring.alerts import Alert


def get_open_alert(alert_name: str) -> Optional[Dict[str, Any]]:
    """Looks up the database audit ledger to determine if there is an active incident marked as OPEN."""
    query = text(
        """
        SELECT alert_id, alert_name, severity, message, triggered_at, resolved_at, status, run_id, stage_name
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
    """Saves an alert into the database using a strict deduplication fence and records correlation metadata."""
    existing = get_open_alert(alert.name)
    if existing:
        return {
            "created": False,
            "alert_id": existing["alert_id"],
            "message": "Suppressed duplicate entry. Existing alert remains OPEN.",
        }

    query = text(
        """
        INSERT INTO alert_history (alert_name, severity, message, status, run_id, stage_name)
        VALUES (:alert_name, :severity, :message, 'OPEN', :run_id, :stage_name)
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
                "run_id": alert.run_id,
                "stage_name": alert.stage_name,
            },
        ).scalar()

        return {
            "created": True,
            "alert_id": alert_id,
            "message": "New operational alert state generated with correlation context.",
        }


def resolve_alert(alert_name: str) -> bool:
    """Transitions an active incident from OPEN to RESOLVED state."""
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
