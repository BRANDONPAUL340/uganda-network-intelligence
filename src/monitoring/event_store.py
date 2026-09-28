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
def publish_quality_event(run_id: int, result: dict) -> str:
    """
    Publishes a quality-check failure as a standardized pipeline event.

    The quality engine supplies the check result, while this wrapper
    translates it into the event-store contract expected by consumers.
    """
    payload = {
        "check_name": result["check_name"],
        "status": result.get("status", "FAIL"),
        "failed_records": result.get("failed_records", 0),
        "check_value": result.get("check_value"),
        "message": result.get(
            "message",
            "Quality validation rule failed."
        ),
        "severity": result.get("severity", "HIGH"),
    }

    return emit_pipeline_event(
        event_type="QUALITY_CHECK_FAILED",
        run_id=run_id,
        producer="quality_engine",
        payload=payload,
    )


def check_event_already_processed(event_id: str, consumer_name: str) -> bool:
    """11 & 12. Idempotency Gate Checker: Inspects processing table to prevent duplicate side effects [INDEX]."""
    query = text(
        """
        SELECT EXISTS (
            SELECT 1 FROM event_processing WHERE event_id = :event_id AND consumer_name = :consumer_name
        );
        """
    )
    with engine.connect() as conn:
        return bool(conn.execute(query, {"event_id": event_id, "consumer_name": consumer_name}).scalar())


def mark_event_as_processed(event_id: str, consumer_name: str) -> None:
    """Logs an event token token entry checkpoint to guarantee idempotency [INDEX]."""
    query = text(
        """
        INSERT INTO event_processing (event_id, consumer_name, processed_at)
        VALUES (:event_id, :consumer_name, CURRENT_TIMESTAMP);
        """
    )
    with engine.begin() as conn:
        conn.execute(query, {"event_id": event_id, "consumer_name": consumer_name})


# ==============================================================================
# 🎯 18 & 19. REUSABLE DOMAIN-SPECIFIC EVENT HANDLERS
# ==============================================================================

def handle_quality_failure_event(event_row, consumer_name: str) -> None:
    """
    25. Domain-Specific Quality Consumer Handler: Unpacks contract payloads asynchronously.
    Routes context directly to the central incident engine using your secure deduplication gate.
    """
    # Parse payload dictionary cleanly regardless of backend string layout types
    payload = event_row.payload if isinstance(event_row.payload, dict) else json.loads(event_row.payload)
    
    # Safely invoke your established incident deduplication gate [1]
    execute_incident_deduplication_gate(
        run_id=int(event_row.run_id),
        check_name=payload["check_name"],
        severity=payload.get("severity", "HIGH"),
        message=payload.get("message", "Quality validation rule failed.")
    )

def handle_unknown_event(event_row, consumer_name: str) -> None:
    """Graceful Fallback: Logs unexpected event variations cleanly without crashing worker loops [INDEX]."""
    print(f"⚠️ Skipped unknown or unmapped event schema type: '{event_row.event_type}' (ID: {event_row.event_id})")


# 19. Centralised Event Routing Lookup Matrix [INDEX]
EVENT_HANDLERS_REGISTRY = {
    "QUALITY_CHECK_FAILED": handle_quality_failure_event
}


def consume_event_store_stream(consumer_name: str = "incident_consumer") -> int:
    """
    15 & 19. Master Event Router Loop: Polls append-only tables chronologically,
    checks idempotency firewalls, and dispatches to registered handler maps [INDEX].
    """
    query = text("SELECT event_id, event_type, run_id, payload FROM pipeline_event_store ORDER BY event_time ASC;")
    processed_count = 0
    
    with engine.connect() as conn:
        events = conn.execute(query).fetchall()
        
    for evt in events:
        evt_id = str(evt.event_id)
        
        # 15. Idempotency Firewall Gate [INDEX]
        if check_event_already_processed(evt_id, consumer_name):
            continue
            
        # 19. Extract matching handler function route cleanly from dictionary registry [INDEX]
        handler = EVENT_HANDLERS_REGISTRY.get(evt.event_type, handle_unknown_event)
        
        # Execute processing logic asynchronously [INDEX]
        handler(evt, consumer_name)
        
        # Lock down transaction state checkpoint token [INDEX]
        mark_event_as_processed(evt_id, consumer_name)
        processed_count += 1
        
    return processed_count


def delete_processing_checkpoint(event_id: str, consumer_name: str) -> None:
    """
    Clears an event's processing state for a single target consumer worker.
    This opens the idempotency gate, priming the event for an intentional replay pass.
    """
    query = text(
        """
        DELETE FROM event_processing 
        WHERE event_id = :event_id AND consumer_name = :consumer_name;
        """
    )
    with engine.begin() as conn:
        conn.execute(query, {"event_id": event_id, "consumer_name": consumer_name})
        print(f"🔄 Checkpoint cleared for Event ID: {event_id} [{consumer_name}]. Ready for replay [1].")


def force_replay_specific_event(event_id: str, consumer_name: str = "incident_consumer") -> bool:
    """
    Extracts a single targeted historical event by its unique UUID token,
    clears its processed state, and forces it back through the Event Router registry.
    """
    # 1. Erase the historical idempotency checkpoint lock row [1]
    delete_processing_checkpoint(event_id, consumer_name)
    
    # 2. Extract the event context from the immutable store [1]
    query = text("SELECT event_id, event_type, run_id, payload FROM pipeline_event_store WHERE event_id = :event_id;")
    with engine.connect() as conn:
        evt = conn.execute(query, {"event_id": event_id}).fetchone()
        
    if not evt:
        print(f"❌ Event ID '{event_id}' not found in the append-only event store.")
        return False
        
    # 3. Force re-route the extracted event back into the handler registry loops [1]
    handler = EVENT_HANDLERS_REGISTRY.get(evt.event_type, handle_unknown_event)
    handler(evt, consumer_name)
    
    # 4. Re-lock the idempotency gate [1]
    mark_event_as_processed(event_id, consumer_name)
    return True


def backfill_events_for_pipeline_run(run_id: int, consumer_name: str = "incident_consumer") -> int:
    """
    Consumer Backfilling: Finds every historical failure event linked to a specific 
    pipeline run ID, clears their checkpoints, and replays them chronologically.
    """
    # Find all events associated with the target run_id [1]
    find_query = text("SELECT event_id FROM pipeline_event_store WHERE run_id = :run_id;")
    with engine.connect() as conn:
        event_rows = conn.execute(find_query, {"run_id": run_id}).fetchall()
        
    replayed_count = 0
    for row in event_rows:
        evt_id = str(row.event_id)
        # Force a recovery pass over each discovered event [1]
        success = force_replay_specific_event(evt_id, consumer_name)
        if success:
            replayed_count += 1
            
    print(f"🚀 Backfill Complete: Replayed {replayed_count} events for Run #{run_id} [1].")
    return replayed_count

