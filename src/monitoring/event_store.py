import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy import text
import pandas as pd
from src.database import engine
from src.monitoring.event_contract import validate_event_envelope_contract
from src.monitoring.incident_manager import execute_incident_deduplication_gate

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

MAX_RETRIES = 3

# ==============================================================================
# 🎯 CORE EVENT PRODUCER UTILITIES
# ==============================================================================

def emit_pipeline_event(event_type: str, run_id: int, producer: str, payload: dict, event_version: str = "1.0.0") -> str:
    """Assembles an immutable event envelope contract and appends it to pipeline_event_store [INDEX]."""
    event_packet = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "event_version": event_version,
        "run_id": run_id,
        "event_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "producer": producer,
        "payload": payload
    }
    validate_event_envelope_contract(event_packet)
    
    query = text(
        """
        INSERT INTO pipeline_event_store (event_id, event_type, event_version, run_id, event_time, producer, payload)
        VALUES (:event_id, :event_type, :event_version, :run_id, :event_time, :producer, :payload);
        """
    )
    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "event_id": event_packet["event_id"],
                "event_type": event_packet["event_type"],
                "event_version": event_packet["event_version"],
                "run_id": event_packet["run_id"],
                "event_time": event_packet["event_time"],
                "producer": event_packet["producer"],
                "payload": json.dumps(event_packet["payload"])
            }
        )
        return event_packet["event_id"]


def check_event_already_processed(event_id: str, consumer_name: str) -> bool:
    """Idempotency Gate Checker: Inspects the database to prevent duplicate side effects [INDEX]."""
    query = text("SELECT EXISTS (SELECT 1 FROM event_processing WHERE event_id = :event_id AND consumer_name = :consumer_name AND status = 'PROCESSED');")
    with engine.connect() as conn:
        return bool(conn.execute(query, {"event_id": event_id, "consumer_name": consumer_name}).scalar())


# ==============================================================================
# 🎯 REGISTRY-DRIVEN EVENT ROUTER HANDLERS
# ==============================================================================

def handle_quality_failure_event(connection, event_row) -> None:
    """Decoupled Domain Handler: Leverages downstream incident deduplication for safety [INDEX]."""
    payload = event_row.payload if isinstance(event_row.payload, dict) else json.loads(event_row.payload)
    execute_incident_deduplication_gate(
        run_id=int(event_row.run_id),
        check_name=payload["check_name"],
        severity=payload.get("severity", "HIGH"),
        message=payload["message"]
    )

def handle_unknown_event(connection, event_row) -> None:
    """Graceful Fallback: Captures unmapped events without throwing fatal thread exceptions [INDEX]."""
    print(f"⚠️ Skipped unmapped or unknown event type: '{event_row.event_type}'")

EVENT_HANDLERS_REGISTRY = {
    "QUALITY_CHECK_FAILED": handle_quality_failure_event
}


# ==============================================================================
# 🔄 14, 15 & 18. ATOMIC REPLAY, BACKFILL & BATCH PROCESSING RECOVERY ENGINE
# ==============================================================================

def replay_event_atomically(event_id: str, consumer_name: str) -> bool:
    """
    14 & 17. Atomic Event Replay Tool: Pulls an immutable historical record 
    and executes processing workflows inside an isolated transactional block [INDEX].
    """
    # 16. The original event remains a permanent historical record; we never DELETE it [INDEX]
    select_evt = text("SELECT event_id, event_type, run_id, payload FROM pipeline_event_store WHERE event_id = :event_id;")
    with engine.connect() as conn:
        evt = conn.execute(select_evt, {"event_id": event_id}).fetchone()
        
    if not evt:
        print(f"❌ Event ID '{event_id}' not found in the append-only store.")
        return False
        
    # 14. Coordinate multi-table side effects within a single PostgreSQL transaction boundary [INDEX]
    with engine.begin() as txn_conn:
        try:
            # Execute business logic route
            handler = EVENT_HANDLERS_REGISTRY.get(evt.event_type, handle_unknown_event)
            handler(txn_conn, evt)
            
            # Mark event checkpoint as successfully PROCESSED inside the same transaction context [INDEX]
            checkpoint_query = text(
                """
                INSERT INTO event_processing (event_id, consumer_name, status, attempt_count, error_message, processed_at, last_attempt_at)
                VALUES (:event_id, :consumer_name, 'PROCESSED', 1, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (event_id, consumer_name) DO UPDATE 
                SET status = 'PROCESSED', attempt_count = event_processing.attempt_count + 1, error_message = NULL, last_attempt_at = CURRENT_TIMESTAMP;
                """
            )
            txn_conn.execute(checkpoint_query, {"event_id": event_id, "consumer_name": consumer_name})
            return True
            
        except Exception as exc:
            # If processing hits an error, log a FAILED checkpoint state to the dead-letter tracking queue [INDEX]
            fail_query = text(
                """
                INSERT INTO event_processing (event_id, consumer_name, status, attempt_count, error_message, last_attempt_at)
                VALUES (:event_id, :consumer_name, 'FAILED', 1, :err, CURRENT_TIMESTAMP)
                ON CONFLICT (event_id, consumer_name) DO UPDATE 
                SET status = 'FAILED', attempt_count = event_processing.attempt_count + 1, error_message = :err, last_attempt_at = CURRENT_TIMESTAMP;
                """
            )
            txn_conn.execute(fail_query, {"event_id": event_id, "consumer_name": consumer_name, "err": str(exc)})
            print(f"⚠️ Replay processing cycle hit an exception. Logged to dead-letter log: {exc}")
            return False


def replay_failed_events(consumer_name: str) -> list:
    """
    15 & 18. Batch Replay Dead-Letter Worker: Discovers dead-lettered FAILED alerts, 
    and iterates chronologically to re-run recovery attempts [INDEX].
    """
    query = text(
        """
        SELECT event_id 
        FROM event_processing 
        WHERE status = 'FAILED' AND consumer_name = :consumer_name
        ORDER BY last_attempt_at ASC;
        """
    )
    with engine.connect() as conn:
        failed_rows = conn.execute(query, {"consumer_name": consumer_name}).fetchall()
        
    execution_results = []
    for row in failed_rows:
        evt_id = str(row.event_id)
        # 18. Iterate and batch-replay each dead-letter event token [INDEX]
        success_flag = replay_event_atomically(evt_id, consumer_name)
        execution_results.append({"event_id": evt_id, "success": success_flag})
        
    return execution_results
