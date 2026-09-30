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
# 🎯 12. COMPOSITE TUPLE REGISTRY MATRIX (Day 150 Version Evolution Engine)
# ==============================================================================

def consume_quality_failure_v1(connection, event_row, payload: dict) -> None:
    """Handles legacy Version 1.0.0 layout contracts safely [INDEX]."""
    execute_incident_deduplication_gate(
        run_id=int(event_row.run_id),
        check_name=payload["check_name"],
        severity="HIGH",
        message=payload["message"]
    )


def consume_quality_failure_v2(connection, event_row, payload: dict) -> None:
    """Handles graduated Version 2.0.0 refactored schema contracts cleanly [INDEX]."""
    execute_incident_deduplication_gate(
        run_id=int(event_row.run_id),
        check_name=payload["check"],
        severity=payload.get("severity", "HIGH"),
        message=payload["error_description"]
    )


# 12. Map complex combinations of type strings and semantic version tags [INDEX]
COMPOSITE_VERSION_HANDLERS_REGISTRY = {
    ("QUALITY_CHECK_FAILED", "1"): consume_quality_failure_v1,
    ("QUALITY_CHECK_FAILED", "1.0.0"): consume_quality_failure_v1,
    ("QUALITY_CHECK_FAILED", "2"): consume_quality_failure_v2,
    ("QUALITY_CHECK_FAILED", "2.0.0"): consume_quality_failure_v2,
}


def handle_quality_failure_event(connection, event_row) -> None:
    """11 & 14. Version Router Gate: Routes payloads using composite tuple lookups [INDEX]."""
    payload = event_row.payload if isinstance(event_row.payload, dict) else json.loads(event_row.payload)
    version = str(event_row.event_version)
    
    # 12. Query the composite tuple lookup matrix cleanly [INDEX]
    handler = COMPOSITE_VERSION_HANDLERS_REGISTRY.get((event_row.event_type, version))
    
    if handler:
        handler(connection, event_row, payload)
    else:
        # 14 & 15. Unsupported contract versions immediately drop out with a clear error [INDEX]
        raise NotImplementedError(f"Unsupported Contract Rule: Version variant '{version}' is not supported for type '{event_row.event_type}'.")


def handle_unknown_event(connection, event_row) -> None:
    """Graceful Fallback: Captures unmapped event types cleanly without crashing [INDEX]."""
    print(f"⚠️ Skipped unmapped or unknown event type: '{event_row.event_type}'")


EVENT_HANDLERS_REGISTRY = {
    "QUALITY_CHECK_FAILED": handle_quality_failure_event
}


# ==============================================================================
# 🔄 ATOMIC REPLAY & RECOVERY ENGINE
# ==============================================================================

def replay_event_atomically(event_id: str, consumer_name: str) -> bool:
    """Atomic Event Replay Tool: Processes historical events safely inside single transactions [INDEX]."""
    select_evt = text("SELECT event_id, event_type, event_version, run_id, payload FROM pipeline_event_store WHERE event_id = :event_id;")
    with engine.connect() as conn:
        evt = conn.execute(select_evt, {"event_id": event_id}).fetchone()
        
    if not evt:
        return False
        
    with engine.begin() as txn_conn:
        try:
            handler = EVENT_HANDLERS_REGISTRY.get(evt.event_type, handle_unknown_event)
            handler(txn_conn, evt)
            
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
            fail_query = text(
                """
                INSERT INTO event_processing (event_id, consumer_name, status, attempt_count, error_message, last_attempt_at)
                VALUES (:event_id, :consumer_name, 'FAILED', 1, :err, CURRENT_TIMESTAMP)
                ON CONFLICT (event_id, consumer_name) DO UPDATE 
                SET status = 'FAILED', attempt_count = event_processing.attempt_count + 1, error_message = :err, last_attempt_at = CURRENT_TIMESTAMP;
                """
            )
            txn_conn.execute(fail_query, {"event_id": event_id, "consumer_name": consumer_name, "err": str(exc)})
            return False
