import sys
from pathlib import Path
from sqlalchemy import text
import pandas as pd
from src.database import engine  # Hooks straight into your centralized connection pool [INDEX]

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def find_open_incident(check_name: str) -> pd.DataFrame:
    """
    Part 6 & 7. Open Incident Selector: Queries the database to discover 
    whether an active 'OPEN' ticket exists for a specific check family [INDEX].
    """
    query = text(
        """
        SELECT incident_id, run_id, check_name, severity, status, message, created_at, occurrence_count
        FROM pipeline_incidents
        WHERE check_name = :check_name AND status = 'OPEN'
        ORDER BY created_at DESC
        LIMIT 1;
    """
    )
    with engine.connect() as conn:
        result = conn.execute(query, {"check_name": check_name}).fetchall()
        # Convert securely to pandas DataFrame to preserve data patterns [INDEX]
        return pd.DataFrame([row._mapping for row in result])


def update_pipeline_incident(incident_id: int, run_id: int, message: str) -> None:
    """
    Increments the occurrence counter and stamps the latest observation 
    parameters on an active outstanding ticket [INDEX].
    """
    query = text(
        """
        UPDATE pipeline_incidents
        SET run_id = :run_id,
            message = :message,
            occurrence_count = occurrence_count + 1,
            last_seen_at = CURRENT_TIMESTAMP
        WHERE incident_id = :incident_id;
    """
    )
    with engine.begin() as conn:
        conn.execute(query, {"incident_id": incident_id, "run_id": run_id, "message": message})


def create_pipeline_incident(run_id: int, check_name: str, severity: str, message: str) -> int:
    """Instantiates a fresh OPEN tracking row inside PostgreSQL [INDEX]."""
    query = text(
        """
        INSERT INTO pipeline_incidents (run_id, check_name, severity, status, message, created_at, last_seen_at, occurrence_count)
        VALUES (:run_id, :check_name, :severity, 'OPEN', :message, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
        RETURNING incident_id;
    """
    )
    with engine.begin() as conn:
        return int(conn.execute(query, {"run_id": run_id, "check_name": check_name, "severity": severity, "message": message}).scalar())


def execute_incident_deduplication_gate(run_id: int, check_name: str, severity: str, message: str) -> int:
    """
    Part 8. The Deduplication Algorithm Engine: Manages incident entries defensively,
    preventing duplicate alert noise across consecutive pipeline executions [INDEX].
    """
    # Look for an outstanding ticket matching this quality check family [INDEX]
    existing_incident_df = find_open_incident(check_name)

    if existing_incident_df.empty:
        # No open ticket found -> create a fresh record
        return create_pipeline_incident(run_id, check_name, severity, message)
    else:
        # Ongoing active breach tracked -> trigger counter increment pass [INDEX]
        incident_id = int(existing_incident_df.iloc[0]["incident_id"])
        update_pipeline_incident(incident_id, run_id, f"[Recurring Failure] {message}")
        return incident_id
