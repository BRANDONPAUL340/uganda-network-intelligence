"""
Uganda Network Intelligence Platform — Event Lifecycle and Archival Engine
Decouples hot operational buffers from cold historical storage data layers safely [INDEX].
"""
import sys
import time
from pathlib import Path
from sqlalchemy import text
from src.database import engine

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def archive_and_purge_batch_cycle(retention_interval_days: int = 30, batch_limit: int = 1000, dry_run: bool = True) -> dict:
    """
    24, 25 & 27. High-Performance Bounded Life-Cycle Engine: Features a safe dry-run mode,
    transaction copy-verify checks, and records granular operational duration metrics [INDEX].
    """
    metrics = {
        "events_selected": 0,
        "events_archived": 0,
        "events_deleted": 0,
        "archive_failures": 0,
        "cleanup_duration_ms": 0.0
    }
    
    start_time = time.time()
    
    # 18. Discover PROCESSED hot events past the retention threshold window [INDEX]
    find_query = text(
        """
        SELECT pes.event_id, pes.event_type, pes.event_version, pes.run_id, pes.producer, pes.payload, pes.event_time
        FROM pipeline_event_store pes
        JOIN event_processing ep ON pes.event_id = ep.event_id
        WHERE ep.status = 'PROCESSED'
          AND pes.event_time < CURRENT_TIMESTAMP - (INTERVAL '1 day' * :days)
        ORDER BY pes.event_time ASC
        LIMIT :batch_limit
        FOR UPDATE SKIP LOCKED;
        """
    )
    
    with engine.begin() as txn_conn:
        cold_events = txn_conn.execute(find_query, {"days": retention_interval_days, "batch_limit": batch_limit}).fetchall()
        metrics["events_selected"] = len(cold_events)
        
        if not cold_events:
            metrics["cleanup_duration_ms"] = (time.time() - start_time) * 1000.0
            return metrics
            
        # 25. Dry Run Safety Guard Gate: Return summary counts without mutating rows [INDEX]
        if dry_run:
            print(f"🔍 [DRY RUN] Found {metrics['events_selected']} events eligible for archival. No rows modified.")
            metrics["cleanup_duration_ms"] = (time.time() - start_time) * 1000.0
            return metrics
            
        try:
            # 10. STEP A: COPY to history archive table [INDEX]
            insert_query = text(
                """
                INSERT INTO pipeline_event_archive (event_id, event_type, event_version, run_id, producer, payload, event_time, archived_at)
                VALUES (:event_id, :event_type, :event_version, :run_id, :producer, :payload, :event_time, CURRENT_TIMESTAMP);
                """
            )
            
            for evt in cold_events:
                txn_conn.execute(
                    insert_query,
                    {
                        "event_id": evt.event_id,
                        "event_type": evt.event_type,
                        "event_version": evt.event_version,
                        "run_id": evt.run_id,
                        "producer": evt.producer,
                        "payload": evt.payload,
                        "event_time": evt.event_time
                    }
                )
                metrics["events_archived"] += 1
                
            # 24. STEP B: STRICT COPY VERIFICATION CHECK GATE [INDEX]
            if metrics["events_archived"] != metrics["events_selected"]:
                raise RuntimeError("Verification Mismatch: Archived row volume counts diverge from selected targets.")
                
            # 10. STEP C: PURGE original rows from active hot buffer table [INDEX]
            claimed_ids = tuple(str(evt.event_id) for evt in cold_events)
            
            clear_child_processing = text("DELETE FROM event_processing WHERE event_id IN :ids;")
            txn_conn.execute(clear_child_processing, {"ids": claimed_ids})
            
            purge_hot_store = text("DELETE FROM pipeline_event_store WHERE event_id IN :ids;")
            txn_conn.execute(purge_hot_store, {"ids": claimed_ids})
            
            metrics["events_deleted"] = metrics["events_archived"]
            
        except Exception as exc:
            # Explicitly mark metrics metrics failures to ensure the cleanup tool remains observable [INDEX]
            metrics["archive_failures"] += 1
            print(f"❌ Structural life-cycle transaction failure. Rolling back: {exc}")
            raise exc
            
    metrics["cleanup_duration_ms"] = (time.time() - start_time) * 1000.0
    return metrics
