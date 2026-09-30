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
# 🎯 21. EXPLICIT COMPATIBILITY POLICY MATRIX
# ==============================================================================
SUPPORTED_VERSIONS = {
    "QUALITY_CHECK_FAILED": {"1", "1.0.0", "2", "2.0.0"}
}


def is_supported_event(event_type: str, event_version: str) -> bool:
    """21. Compatibility Gate: Asserts whether a schema contract version is supported [INDEX]."""
    versions = SUPPORTED_VERSIONS.get(event_type, set())
    return str(event_version) in versions


# ==============================================================================
# 🎯 CORE EVENT PRODUCER UTILITIES
# ==============================================================================

from src.monitoring.event_contract import validate_event, EventContractValidationError

def emit_pipeline_event(event_type: str, run_id: int, producer: str, payload: dict, event_version: int = 1) -> str:
    """
    24 & 25. Producer Validation Firewall: Builds an event envelope, enforces contract checks 
    upstream, and inserts the record into PostgreSQL ONLY if it passes validation [INDEX].
    """
    event_packet = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "event_version": event_version,
        "run_id": run_id,
        "event_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "producer": producer,
        "payload": payload
    }
    
    # 24 & 25. Validate contract BEFORE inserting into PostgreSQL [INDEX]
    validation_result = validate_event(event_packet)
    if not validation_result["valid"]:
        raise EventContractValidationError(f"Upstream Ingestion Blocked: Malformed data payload rejected. Errors: {validation_result['errors']}")
    
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


def mark_event_as_processed(event_id: str, consumer_name: str, status: str = "PROCESSED", error_message: str = None) -> None:
    """Logs or updates an entry inside the event_processing ledger to guarantee idempotency [INDEX]."""
    query = text(
        """
        INSERT INTO event_processing (event_id, consumer_name, status, error_message, processed_at, last_attempt_at)
        VALUES (:event_id, :consumer_name, :status, :error_message, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (event_id, consumer_name) DO UPDATE 
        SET status = :status, error_message = :error_message, last_attempt_at = CURRENT_TIMESTAMP;
        """
    )
    with engine.begin() as conn:
        conn.execute(query, {"event_id": event_id, "consumer_name": consumer_name, "status": status, "error_message": error_message})


# ==============================================================================
# 🎯 COMPOSITE TUPLE REGISTRY HANDLERS
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


COMPOSITE_VERSION_HANDLERS_REGISTRY = {
    ("QUALITY_CHECK_FAILED", "1"): consume_quality_failure_v1,
    ("QUALITY_CHECK_FAILED", "1.0.0"): consume_quality_failure_v1,
    ("QUALITY_CHECK_FAILED", "2"): consume_quality_failure_v2,
    ("QUALITY_CHECK_FAILED", "2.0.0"): consume_quality_failure_v2,
}


def handle_quality_failure_event(connection, event_row) -> None:
    """11, 14 & 21. Version Router Gate: Routes payloads safely via lookup policies [INDEX]."""
    payload = event_row.payload if isinstance(event_row.payload, dict) else json.loads(event_row.payload)
    version = str(event_row.event_version)
    
    # 21. Explicitly check compatibility matrix before executing consumer logic [INDEX]
    if not is_supported_event(event_row.event_type, version):
        raise NotImplementedError(f"Unsupported Contract Rule: Version variant '{version}' is not supported for type '{event_row.event_type}'.")
        
    handler = COMPOSITE_VERSION_HANDLERS_REGISTRY.get((event_row.event_type, version))
    if handler:
        handler(connection, event_row, payload)
    else:
        raise ValueError(f"Contract Error: Missing specific handler for supported version variant '{version}'.")


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
