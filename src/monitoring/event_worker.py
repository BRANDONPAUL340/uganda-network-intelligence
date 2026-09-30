"""
Uganda Network Intelligence Platform — Configurable Background Event Worker Daemon
Features graceful OS termination intercepts, throughput calculations, and adaptive polling [INDEX].
"""
import os
import sys
import json
import time
import signal
from datetime import datetime
from pathlib import Path
from sqlalchemy import text
from src.database import engine
from sqlalchemy import text, bindparam

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Standardized Operational Tuning Parametric Configuration Matrix [INDEX]
WORKER_CONFIG = {
    "poll_interval_seconds": 5.0,
    "batch_size": 100,
    "max_attempts": 3,
    "lease_seconds": 60
}

worker_shutdown_requested = False


def handle_termination_signal(signum, frame):
    """27. Graceful Intercept Handler: Captures incoming OS interrupt signals (SIGINT/SIGTERM) [INDEX]."""
    global worker_shutdown_requested
    print(f"\n🛑 System Signal {signum} Caught! Initializing graceful shutdown procedures...")
    worker_shutdown_requested = True


signal.signal(signal.SIGINT, handle_termination_signal)
try:
    signal.signal(signal.SIGTERM, handle_termination_signal)
except AttributeError:
    pass


def get_unique_worker_identity() -> str:
    """13. Worker Identity: Generates a distinct local execution identifier string [INDEX]."""
    return f"worker-daemon-pid-{os.getpid()}"


def emit_worker_heartbeat(status: str, processed_delta: int = 0, errors_delta: int = 0) -> None:
    """14 & 23. Persistent Heartbeat Emitter: Stores operational metrics directly in PostgreSQL [INDEX]."""
    worker_id = get_unique_worker_identity()
    query = text(
        """
        INSERT INTO pipeline_worker_heartbeats (worker_id, status, last_heartbeat_at, events_processed, errors_count)
        VALUES (:worker_id, :status, CURRENT_TIMESTAMP, :p_delta, :e_delta)
        ON CONFLICT (worker_id) DO UPDATE 
        SET status = :status,
            last_heartbeat_at = CURRENT_TIMESTAMP,
            events_processed = pipeline_worker_heartbeats.events_processed + :p_delta,
            errors_count = pipeline_worker_heartbeats.errors_count + :e_delta;
        """
    )
    with engine.begin() as conn:
        conn.execute(query, {"worker_id": worker_id, "status": status, "p_delta": processed_delta, "e_delta": errors_delta})


def reclaim_stale_worker_leases(consumer_name: str) -> int:
    """Stale Lease Reclaimer: Reverts expired PROCESSING leases back to RETRY [INDEX]."""
    query = text(
        f"""
        UPDATE event_processing
        SET status = 'RETRY',
            error_message = 'Lease Expired: Worker node failed to report status within timeout window.',
            next_attempt_at = CURRENT_TIMESTAMP + INTERVAL '10 seconds'
        WHERE status = 'PROCESSING'
          AND consumer_name = :consumer_name
          AND claimed_at < CURRENT_TIMESTAMP - INTERVAL '{WORKER_CONFIG["lease_seconds"]} seconds'
        RETURNING event_id;
        """
    )
    with engine.begin() as conn:
        reclaimed_rows = conn.execute(query, {"consumer_name": consumer_name}).fetchall()
        return len(reclaimed_rows)


def process_concurrent_event_batch(consumer_name: str, batch_size: int = 10) -> dict:
    """Claims available events using atomic CTE constructs and processes them safely outside locks [INDEX]."""
    worker_id = get_unique_worker_identity()
    reclaim_stale_worker_leases(consumer_name)
    
    cte_claim_query = text(
    """
    WITH claimed AS (
        SELECT pes.event_id
        FROM pipeline_event_store pes
        LEFT JOIN event_processing ep
            ON pes.event_id = ep.event_id
            AND ep.consumer_name = :consumer_name
        WHERE ep.status IS NULL
           OR (
               ep.status IN ('PENDING', 'RETRY')
               AND (
                   ep.next_attempt_at IS NULL
                   OR ep.next_attempt_at <= CURRENT_TIMESTAMP
               )
           )
        ORDER BY pes.event_time ASC
        LIMIT :batch_size
        FOR UPDATE OF pes SKIP LOCKED
    )
    INSERT INTO event_processing (
        event_id,
        consumer_name,
        status,
        attempt_count,
        claimed_by,
        claimed_at,
        last_attempt_at
    )
    SELECT
        event_id,
        :consumer_name,
        'PROCESSING',
        1,
        :worker_id,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    FROM claimed
    ON CONFLICT (event_id, consumer_name) DO UPDATE
    SET status = 'PROCESSING',
        claimed_by = :worker_id,
        claimed_at = CURRENT_TIMESTAMP,
        attempt_count = event_processing.attempt_count + 1,
        last_attempt_at = CURRENT_TIMESTAMP
    RETURNING event_id;
    """
)
    
    metrics = {"received": 0, "processed": 0, "failed": 0, "skipped": 0}
    
    with engine.begin() as txn_conn:
        claimed_rows = txn_conn.execute(cte_claim_query, {
            "consumer_name": consumer_name, 
            "batch_size": batch_size, 
            "worker_id": worker_id
        }).fetchall()
        
        claimed_ids = [str(row.event_id) for row in claimed_rows]
        metrics["received"] = len(claimed_ids)
        
    if not claimed_ids:
        return metrics
        
    from src.monitoring.event_store import EVENT_HANDLERS_REGISTRY, handle_unknown_event, check_event_already_processed
    
    fetch_query = text(
        """
        SELECT event_id, event_type, run_id, payload
        FROM pipeline_event_store
        WHERE event_id IN :ids;
        """
    ).bindparams(bindparam("ids", expanding=True))

    with engine.connect() as conn:
        claimed_events = conn.execute(
            fetch_query,
            {"ids": list(claimed_ids)}
        ).fetchall()

    for evt in claimed_events:
        evt_id = str(evt.event_id)

        if check_event_already_processed(evt_id, consumer_name):
            metrics["skipped"] += 1
            continue

        try:
            with engine.begin() as work_conn:
                handler = EVENT_HANDLERS_REGISTRY.get(
                    evt.event_type,
                    handle_unknown_event
                )
                handler(work_conn, evt)

                success_query = text(
                    """
                    UPDATE event_processing
                    SET status = 'PROCESSED',
                        processed_at = CURRENT_TIMESTAMP,
                        claimed_by = NULL
                    WHERE event_id = :event_id
                      AND consumer_name = :consumer_name;
                    """
                )

                work_conn.execute(
                    success_query,
                    {
                        "event_id": evt_id,
                        "consumer_name": consumer_name
                    }
                )

                metrics["processed"] += 1

        except Exception as exc:
            with engine.begin() as fail_conn:
                fail_query = text(
                    """
                    UPDATE event_processing
                    SET status = 'FAILED',
                        error_message = :err,
                        claimed_by = NULL
                    WHERE event_id = :event_id
                      AND consumer_name = :consumer_name;
                    """
                )

                fail_conn.execute(
                    fail_query,
                    {
                        "event_id": evt_id,
                        "consumer_name": consumer_name,
                        "err": str(exc)
                    }
                )

                metrics["failed"] += 1

    return metrics

def run_continuous_worker_service(
    consumer_name: str = "incident_consumer",
    poll_interval: float = None,
    batch_size: int = None,
    max_loops: int = None,
) -> None:
    """
    25, 26, 27 & 31. Adaptive Continuous Worker: Polls the event store at scheduled intervals.
    Employs adaptive polling, metrics tracking, and graceful signal handlers [INDEX].
    """
    global worker_shutdown_requested
    worker_id = get_unique_worker_identity()
    loops = 0
    
    # 26. Advertise STARTING state
    emit_worker_heartbeat(status="STARTING")
    
    while not worker_shutdown_requested:
        if max_loops is not None and loops >= max_loops:
            break
        loops += 1
        
        start_time = time.time()
        
        try:
            # 30. Run worker cycle once over a single batch chunk [INDEX]
            metrics = process_concurrent_event_batch(
    consumer_name=consumer_name,
    batch_size=batch_size if batch_size is not None else WORKER_CONFIG["batch_size"]
)
            
            elapsed_seconds = max(time.time() - start_time, 0.001)
            throughput = metrics["processed"] / elapsed_seconds
            
            # 26. Advertise RUNNING state alongside updated processing metrics [INDEX]
            emit_worker_heartbeat(
                status="RUNNING", 
                processed_delta=metrics["processed"], 
                errors_delta=metrics["failed"]
            )
            
            if metrics["received"] > 0:
                print(f"⏳ [{datetime.now().strftime('%H:%M:%S')}] Cycle #{loops} | Throughput: {throughput:.1f} events/sec | Handled: {metrics['processed']} success.")
                
            # 25. Adaptive Polling: If events were processed, poll again immediately without waiting [INDEX]
            effective_batch_size = batch_size if batch_size is not None else WORKER_CONFIG["batch_size"]

            if metrics["received"] == effective_batch_size and not worker_shutdown_requested:
                continue
                
        except Exception as exc:
            print(f"❌ Core background worker thread sustained an infrastructure crash loop: {exc}")
            emit_worker_heartbeat(status="ERROR", errors_delta=1)
            
        # Standard poll interval sleep window [INDEX]
        if not worker_shutdown_requested:
           effective_poll_interval = (
    poll_interval
    if poll_interval is not None
    else WORKER_CONFIG["poll_interval_seconds"]
)

    time.sleep(WORKER_CONFIG["poll_interval_seconds"])
        
    # 26 & 27. Advertise clean STOPPED state before final thread exit [INDEX]
    emit_worker_heartbeat(status="STOPPED")
    print("🏁 Active Worker Execution Context terminated gracefully.")


def run_worker_cycle_once(consumer_name: str = "incident_consumer") -> dict:
    return process_concurrent_event_batch(consumer_name, batch_size=WORKER_CONFIG["batch_size"])
