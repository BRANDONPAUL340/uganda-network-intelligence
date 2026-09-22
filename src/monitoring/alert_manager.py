import sys
from pathlib import Path

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.monitoring.alerts import Alert
from src.monitoring.alert_store import save_alert, resolve_alert, get_open_alert


def process_alert_condition(alert: Alert) -> dict:
    """
    Orchestrates incident ingestion tracking by validating active alerts against 
    the deduplication fence before committing new rows [INDEX].
    """
    if not alert:
        return {"created": False, "alert_id": None, "message": "No active alert triggered."}
        
    return save_alert(alert)


def resolve_alert_condition(alert_name: str) -> dict:
    """
    Orchestrates the resolution phase of an active system anomaly, updating 
    incident states atomically across your database views [INDEX].
    """
    open_incident = get_open_alert(alert_name)
    if not open_incident:
        return {
            "resolved": False, 
            "alert_id": None, 
            "message": f"No active OPEN alert found for name: '{alert_name}'."
        }
        
    was_resolved = resolve_alert(alert_name)
    return {
        "resolved": was_resolved,
        "alert_id": open_incident["alert_id"],
        "message": f"Incident '{alert_name}' successfully moved to RESOLVED state." if was_resolved else "State update failed."
    }
