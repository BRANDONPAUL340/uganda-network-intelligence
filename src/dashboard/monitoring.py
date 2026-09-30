import pandas as pd
import streamlit as st
from sqlalchemy import text
from src.database import engine
from src.dashboard.data import read_query



@st.cache_data(ttl=15)
def get_recent_runs(limit: int = 10) -> pd.DataFrame:
    """Retrieves a rolling summary list of recent pipeline runs [INDEX]."""
    query = """
        SELECT run_id, pipeline_name, status, started_at, completed_at, records_processed
        FROM pipeline_runs
        ORDER BY run_id DESC
        LIMIT :limit;
    """
    return read_query(query, "get_recent_runs", params={"limit": limit})


@st.cache_data(ttl=15)
def get_failed_runs() -> pd.DataFrame:
    """
    4. Failed Runs Query: Retrieves all executions marked as FAILED 
    to isolate fatal application-level errors [INDEX].
    """
    query = """
        SELECT run_id, pipeline_name, status, started_at, completed_at, error_message
        FROM pipeline_runs
        WHERE status = 'FAILED'
        ORDER BY started_at DESC;
    """
    return read_query(query, "get_failed_runs")


@st.cache_data(ttl=15)
def get_failed_steps() -> pd.DataFrame:
    """
    5. Failed Steps Query: Retrieves individual task failures from pipeline_steps 
    to pinpoint exactly where a bottleneck or crash occurred [INDEX].
    """
    query = """
        SELECT run_id, step_name, status, records_processed, started_at, completed_at, error_message
        FROM pipeline_steps
        WHERE status = 'FAILED'
        ORDER BY started_at DESC;
    """
    return read_query(query, "get_failed_steps")


@st.cache_data(ttl=15)
def get_run_summary() -> pd.DataFrame:
    """
    6. Run Summary KPI Query: Computes aggregate platform execution statistics 
    using efficient in-database filtering passes [INDEX].
    """
    query = """
        SELECT
            COUNT(*) AS total_runs,
            COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful_runs,
            COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_runs
        FROM pipeline_runs;
    """
    return read_query(query, "get_run_summary")


@st.cache_data(ttl=15)
def get_open_alerts() -> pd.DataFrame:
    """
    Extracts all currently unresolved incidents from the audit ledger table 
    to populate high-priority alert cards [INDEX].
    """
    query = """
        SELECT alert_id, alert_name, severity, message, triggered_at, status
        FROM alert_history
        WHERE status = 'OPEN'
        ORDER BY triggered_at DESC;
    """
    return read_query(query, "get_open_alerts")


@st.cache_data(ttl=15)
def get_recent_alerts(limit: int = 20) -> pd.DataFrame:
    """
    Extracts recent historical incidents, allowing operators to audit 
    full operational lifecycles from OPEN to RESOLVED [INDEX].
    """
    query = """
        SELECT alert_id, alert_name, severity, message, triggered_at, resolved_at, status
        FROM alert_history
        ORDER BY triggered_at DESC
        LIMIT :limit;
    """
    return read_query(query, "get_recent_alerts", params={"limit": limit})


@st.cache_data(ttl=15)
def get_alert_summary_by_status() -> pd.DataFrame:
    """Groups incident frequencies by lifecycle state tokens [INDEX]."""
    query = """
        SELECT status, COUNT(*) AS alert_count
        FROM alert_history
        GROUP BY status
        ORDER BY status;
    """
    return read_query(query, "get_alert_summary_by_status")


@st.cache_data(ttl=15)
def get_alert_summary_by_severity() -> pd.DataFrame:
    """Groups open incident metrics by severity tiers to feed triage grids [INDEX]."""
    query = """
        SELECT severity, COUNT(*) AS alert_count
        FROM alert_history
        WHERE status = 'OPEN'
        GROUP BY severity
        ORDER BY severity;
    """
    return read_query(query, "get_alert_summary_by_severity")
@st.cache_data(ttl=15)
def get_run_details(run_id: int) -> pd.DataFrame:
    """
    12. Ingestion Run Investigation: Retrieves execution metadata parameters 
    for a specific batch from the public.pipeline_runs table [INDEX].
    """
    query = """
        SELECT run_id, pipeline_name, status, started_at, completed_at, 
               records_processed, duration_seconds, current_stage, deployment_version
        FROM pipeline_runs
        WHERE run_id = :run_id;
    """
    return read_query(query, "get_run_details", params={"run_id": run_id})


@st.cache_data(ttl=15)
def get_stage_details(run_id: int) -> pd.DataFrame:
    """
    13. Sub-Stage Task Investigation: Extracts the complete execution breakdown 
    and task status logs associated with a given runtime thread [INDEX].
    """
    query = """
        SELECT stage_run_id, stage_name, status, started_at, completed_at, duration_seconds
        FROM pipeline_stage_runs
        WHERE run_id = :run_id
        ORDER BY started_at ASC;
    """
    return read_query(query, "get_stage_details", params={"run_id": run_id})


@st.cache_data
def get_run_lineage(run_id):
    query = """
        SELECT lineage_id,
               run_id,
               stage_run_id,
               source_table,
               target_table,
               records_processed,
               created_at
        FROM pipeline_lineage
        WHERE run_id = :run_id
        ORDER BY created_at;
    """
    return read_query(query, "get_run_lineage", params={"run_id": run_id})


@st.cache_data(ttl=15)
def get_incident_complete_context(selected_alert_id: int) -> pd.DataFrame:
    """
    Master Incident Correlation Query: Unifies alert indicators with their
    matching pipeline run details, execution timelines, and processed row metrics.
    """
    query = """
        SELECT
            a.alert_id,
            a.alert_name,
            a.severity,
            a.message,
            a.status,
            a.triggered_at,
            a.resolved_at,
            a.run_id,
            a.stage_name,
            p.pipeline_name,
            p.started_at,
            p.completed_at,
            p.status AS pipeline_status,
            p.records_processed,
            p.records_read,
            p.records_rejected,
            p.records_inserted,
            p.current_stage
        FROM alert_history a
        LEFT JOIN pipeline_runs p ON a.run_id = p.run_id
        WHERE a.alert_id = :alert_id;
    """
    return read_query(
        query,
        "get_incident_complete_context",
        params={"alert_id": selected_alert_id},
    )

@st.cache_data(ttl=15)
def get_current_processing_watermarks() -> pd.DataFrame:
    """
    15. Incremental Watermark Context Fetcher: Pulls active data offsets 
    per layer block from the public.processing_watermarks tracking table [INDEX].
    """
    query = """
        SELECT stage_name, source_name, last_raw_measurement_id, updated_at
        FROM processing_watermarks
        ORDER BY stage_name ASC, source_name ASC;
    """
    return read_query(query, "get_current_processing_watermarks")

@st.cache_data(ttl=15)
def get_recent_pipeline_runs(limit: int = 10) -> pd.DataFrame:
    """
    10. Summary Metrics: Fetches recent pipeline batch runs 
    from the centralized database monitoring view [1, 2].
    """
    query = """
        SELECT DISTINCT run_id, pipeline_name, pipeline_status, 
               pipeline_started_at, pipeline_completed_at, pipeline_duration_seconds
        FROM pipeline_monitoring_summary
        ORDER BY run_id DESC
        LIMIT :limit;
    """
    return read_query(query, "get_recent_pipeline_runs", params={"limit": limit})


@st.cache_data(ttl=15)
def get_step_level_durations(run_id: int) -> pd.DataFrame:
    """
    6. Duration Analytics: Retrieves task execution durations and processed 
    record counts for a specific pipeline iteration run [1, 2].
    """
    query = """
        SELECT step_name, step_status, records_processed,
               EXTRACT(EPOCH FROM (step_completed_at - step_started_at)) AS step_duration_seconds,
               error_message
        FROM pipeline_monitoring_summary
        WHERE run_id = :run_id AND step_name IS NOT NULL
        ORDER BY step_id ASC;
    """
    return read_query(query, "get_step_level_durations", params={"run_id": run_id})
@st.cache_data(ttl=15)
def get_step_durations() -> pd.DataFrame:
    """
    10. Step Durations Tracker: Extracts exact execution intervals and record counts
    per stage layer from pipeline_steps to monitor long-term performance drift [INDEX].
    """
    query = """
        SELECT
            run_id,
            step_name,
            status,
            records_processed,
            started_at,
            completed_at,
            EXTRACT(EPOCH FROM (completed_at - started_at)) AS duration_seconds
        FROM pipeline_steps
        WHERE completed_at IS NOT NULL
        ORDER BY run_id DESC, started_at ASC;
    """
    return read_query(query, "get_step_durations")
@st.cache_data(ttl=15)
def get_last_successful_run() -> pd.DataFrame:
    """
    13. Last Successful Run Fetcher: Isolates the newest batch run record 
    that achieved a SUCCESS status to drive visibility cards [INDEX].
    """
    query = """
        SELECT run_id, pipeline_name, completed_at, records_processed, deployment_version
        FROM pipeline_runs
        WHERE status = 'SUCCESS'
        ORDER BY completed_at DESC
        LIMIT 1;
    """
    return read_query(query, "get_last_successful_run")
@st.cache_data(ttl=15)
def get_available_runs() -> pd.DataFrame:
    """
    4. Available Run Selection Query: Retrieves the complete structural index 
    of historical runs from pipeline_runs to drive dropdown filter select lists [INDEX].
    """
    query = """
        SELECT run_id, pipeline_name, status, started_at, completed_at
        FROM pipeline_runs
        ORDER BY run_id DESC;
    """
    return read_query(query, "get_available_runs")


@st.cache_data(ttl=15)
def get_run_step_durations(run_id: int) -> pd.DataFrame:
    """
    14. Run Step Duration Tracker: Extracts explicit runtime execution intervals 
    and row counts chronologically for a targeted parent execution run [INDEX].
    """
    query = """
        SELECT
            step_name,
            status,
            records_processed,
            completed_at - started_at AS duration,
            EXTRACT(EPOCH FROM (completed_at - started_at)) AS duration_seconds,
            started_at,
            completed_at
        FROM pipeline_steps
        WHERE run_id = :run_id AND completed_at IS NOT NULL
        ORDER BY step_id ASC;
    """
    return read_query(query, "get_run_step_durations", params={"run_id": run_id})
@st.cache_data(ttl=15)
def get_quality_summary() -> pd.DataFrame:
    """
    Returns the aggregate data quality summary used by the dashboard.
    This is a compatibility wrapper around get_quality_run_summary().
    """
    return get_quality_run_summary()

@st.cache_data(ttl=15)
def get_quality_failure_rates() -> pd.DataFrame:
    """
    4. Failure Rate Analytics: Computes the longitudinal failure percentage rate 
    per check family to highlight persistent pipeline data quality issues [INDEX].
    """
    query = """
        SELECT check_name, COUNT(*) AS total_checks,
               COUNT(*) FILTER (WHERE status = 'FAIL') AS failures,
               ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'FAIL') / NULLIF(COUNT(*), 0), 2) AS failure_rate_pct
        FROM data_quality_results
        GROUP BY check_name
        ORDER BY failure_rate_pct DESC;
    """
    return read_query(query, "get_quality_failure_rates")


@st.cache_data(ttl=15)
def get_latest_quality_status() -> pd.DataFrame:
    """
    8. High-Watermark Quality Selector: Employs a window function to partition and extract 
    the absolute latest status snapshot entry for every unique quality check [INDEX].
    """
    query = """
        SELECT
    check_name,
    status,
    failure_rate_pct AS check_value,
    failed_records,
    checked_at
        FROM (
            SELECT dqr.*,
                   ROW_NUMBER() OVER (
                       PARTITION BY check_name 
                       ORDER BY checked_at DESC, quality_result_id DESC
                   ) AS rn
            FROM data_quality_results dqr
        ) x
        WHERE rn = 1
        ORDER BY check_name;
    """
    return read_query(query, "get_latest_quality_status")


@st.cache_data(ttl=15)
def get_quality_run_summary() -> pd.DataFrame:
    """
    6. Run Quality Summary: Condenses the quality compliance profile across 
    individual run batches to output overall health ratios for dashboard cards [INDEX].
    """
    query = """
        SELECT run_id, COUNT(*) AS total_checks,
               COUNT(*) FILTER (WHERE status = 'PASS') AS passed,
               COUNT(*) FILTER (WHERE status = 'WARNING') AS warnings,
               COUNT(*) FILTER (WHERE status = 'FAIL') AS failures
        FROM data_quality_results
        GROUP BY run_id
        ORDER BY run_id DESC;
    """
    return read_query(query, "get_quality_run_summary")



@st.cache_data(ttl=15)
def get_quality_history() -> pd.DataFrame:
    """
    7. Chronological Quality History Log: Pulls a rolling chronological 
    timeline list of all logged quality metrics across pipeline executions [INDEX].
    """
    query = """
        SELECT
            run_id,
            check_name,
            status,
            check_value,
            failed_records,
            checked_at
        FROM data_quality_results
        ORDER BY checked_at ASC;
    """
    return read_query(query, "get_quality_history")

@st.cache_data(ttl=15)
def get_run_details(run_id: int) -> pd.DataFrame:
    """
    7. Parameterized Run Details: Extracts top-level execution summary metadata 
    for a single selected run execution context [INDEX].
    """
    query = """
        SELECT run_id, pipeline_name, status, started_at, completed_at, 
               records_processed, error_message
        FROM pipeline_runs
        WHERE run_id = :run_id;
    """
    return read_query(query, "get_run_details", params={"run_id": run_id})


@st.cache_data(ttl=15)
def get_run_steps(run_id: int) -> pd.DataFrame:
    """
    8. Parameterized Step Selector: Retrieves granular sub-stage task runtime entries 
    and log parameters matching the operator's chosen Parent Run ID [INDEX].
    """
    query = """
        SELECT step_id, run_id, step_name, status, records_processed, 
               started_at, completed_at, error_message
        FROM pipeline_steps
        WHERE run_id = :run_id
        ORDER BY step_id ASC;
    """
    return read_query(query, "get_run_steps", params={"run_id": run_id})
@st.cache_data(ttl=15)
def get_run_quality(run_id: int) -> pd.DataFrame:
    """
    9. Parameterized Run Quality: Extracts data quality validation scores, 
    actual values, and messages filtered exclusively by a chosen Run ID [INDEX].
    """
    query = """
        SELECT
            quality_id,
            run_id,
            check_name,
            status,
            records_checked,
            failed_records,
            check_value,
            message,
            checked_at
        FROM data_quality_results
        WHERE run_id = :run_id
        ORDER BY quality_id ASC;
    """
    return read_query(query, "get_run_quality", params={"run_id": run_id})

@st.cache_data(ttl=15)
def get_open_incidents() -> pd.DataFrame:
    """
    12 & 21. Open Incidents Finder: Retrieves all outstanding, unresolved tickets 
    from pipeline_incidents to populate the interactive command center [INDEX].
    """
    query = """
        SELECT incident_id, run_id, check_name, severity, status, message, created_at
        FROM pipeline_incidents
        WHERE status = 'OPEN'
        ORDER BY created_at DESC;
    """
    return read_query(query, "get_open_incidents")


@st.cache_data(ttl=15)
def get_incident_mttr_metrics() -> pd.DataFrame:
    """
    19. MTTR Aggregator: Employs database interval math to compute the mean time 
    to resolution across all closed engineering incidents [INDEX].
    """
    query = """
        SELECT 
            COUNT(*) AS resolved_count,
            AVG(resolved_at - created_at) AS raw_average_time,
            EXTRACT(EPOCH FROM AVG(resolved_at - created_at)) / 60.0 AS avg_resolution_minutes
        FROM pipeline_incidents
        WHERE resolved_at IS NOT NULL;
    """
    return read_query(query, "get_incident_mttr_metrics")


@st.cache_data(ttl=15)
def get_run_incidents(run_id: int) -> pd.DataFrame:
    """
    21. Parameterized Incident Drill-Down: Extracts issues linked specifically 
    to an operator's selected parent run context ID [INDEX].
    """
    query = """
        SELECT incident_id, check_name, severity, status, message, created_at, resolved_at
        FROM pipeline_incidents
        WHERE run_id = :run_id
        ORDER BY incident_id ASC;
    """
    return read_query(query, "get_run_incidents", params={"run_id": run_id})

@st.cache_data(ttl=15)
def get_open_incident_count() -> int:
    """
    Part 5. Open Incident Counter: Returns the absolute number of currently 
    unresolved data platform issues needing engineering triage [INDEX].
    """
    query = """
        SELECT COUNT(*) AS open_incidents
        FROM pipeline_incidents
        WHERE status = 'OPEN';
    """
    df = read_query(query, "get_open_incident_count")
    if not df.empty:
        return int(df.iloc[0]["open_incidents"])
    return 0


@st.cache_data(ttl=15)
def get_open_incidents_by_severity() -> pd.DataFrame:
    """
    Part 6. Severity Stratification: Aggregates open issues by operational severity categories 
    (LOW, MEDIUM, HIGH) to feed the dashboard summary cards [INDEX].
    """
    query = """
        SELECT severity, COUNT(*) AS total
        FROM pipeline_incidents
        WHERE status = 'OPEN'
        GROUP BY severity
        ORDER BY severity;
    """
    return read_query(query, "get_open_incidents_by_severity")
@st.cache_data(ttl=15)
def get_incident_date_trends() -> pd.DataFrame:
    """
    20. Incidents by Day: Groups historical entries by calendar date 
    to isolate operational windows where pipeline quality deteriorated [INDEX].
    """
    query = """
        SELECT DATE(created_at) AS incident_date, COUNT(*) AS incidents_created
        FROM pipeline_incidents
        GROUP BY DATE(created_at)
        ORDER BY incident_date ASC;
    """
    return read_query(query, "get_incident_date_trends")


@st.cache_data(ttl=15)
def get_incident_status_ratios() -> pd.DataFrame:
    """
    20. Resolved vs Open: Compares active open issues against closed historical 
    records to monitor engineering backlog and cleanup speeds [INDEX].
    """
    query = """
        SELECT status, COUNT(*) AS total
        FROM pipeline_incidents
        GROUP BY status
        ORDER BY status ASC;
    """
    return read_query(query, "get_incident_status_ratios")
@st.cache_data(ttl=15)
def get_incident_notifications(incident_id: int) -> pd.DataFrame:
    """Pulls the communication dispatch audit history logs linked to a targeted incident [INDEX]."""
    query = """
        SELECT notification_id, channel, delivery_status, recipient, error_message, dispatched_at
        FROM pipeline_notification_logs
        WHERE incident_id = :incident_id
        ORDER BY notification_id DESC;
    """
    return read_query(query, "get_incident_notifications", params={"incident_id": incident_id})

@st.cache_data(ttl=15)
def get_failed_events_queue(consumer_name: str = "incident_consumer") -> pd.DataFrame:
    """
    15 & 19. Dead-Letter Queue Extractor: Retrieves all failed processing attempts 
    for a targeted consumer family to populate the active visual recovery deck [INDEX].
    """
    query = """
        SELECT ep.event_id, pes.event_type, pes.run_id, ep.attempt_count, 
               ep.error_message, ep.last_attempt_at
        FROM event_processing ep
        JOIN pipeline_event_store pes ON ep.event_id = pes.event_id
        WHERE ep.status = 'FAILED' AND ep.consumer_name = :consumer_name
        ORDER BY ep.last_attempt_at DESC;
    """
    return read_query(query, "get_failed_events_queue", params={"consumer_name": consumer_name})


@st.cache_data(ttl=15)
def get_run_event_stream_ledger(run_id: int) -> pd.DataFrame:
    """
    19. Run-Isolated Event Stream: Fetches all historical event envelope metadata 
    linked to a specific pipeline execution run ID to enable targeted backfills [INDEX].
    """
    query = """
        SELECT event_id, event_type, event_version, producer, event_time
        FROM pipeline_event_store
        WHERE run_id = :run_id
        ORDER BY event_time ASC;
    """
    return read_query(query, "get_run_event_stream_ledger", params={"run_id": run_id})

@st.cache_data(ttl=15)
def get_event_processing_status_metrics() -> pd.DataFrame:
    """
    19. Processing Status Summary: Aggregates total metrics by lifecycle state 
    from event_processing to populate dashboard counter blocks [INDEX].
    """
    query = """
        SELECT status, COUNT(*) AS total
        FROM event_processing
        GROUP BY status
        ORDER BY status ASC;
    """
    return read_query(query, "get_event_processing_status_metrics")


@st.cache_data(ttl=15)
def get_event_stream_lag_ledger() -> pd.DataFrame:
    """
    20. Event Lag Tracker: Computes the precise chronological age of events 
    waiting in pipeline_event_store to audit background worker performance [INDEX].
    """
    query = """
        SELECT event_id, event_type, event_time,
               CURRENT_TIMESTAMP - event_time AS event_age,
               EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - event_time)) AS lag_seconds
        FROM pipeline_event_store
        ORDER BY event_time DESC
        LIMIT 20;
    """
    return read_query(query, "get_event_stream_lag_ledger")

@st.cache_data(ttl=5)
def get_worker_cluster_heartbeat_ledger() -> pd.DataFrame:
    """
    15. Worker Health Audit: Queries active worker heartbeats and computes 
    exact age intervals to identify stale cluster nodes cleanly [INDEX].
    """
    query = """
        SELECT worker_id, status, last_heartbeat_at,
               CURRENT_TIMESTAMP - last_heartbeat_at AS heartbeat_age,
               events_processed, errors_count
        FROM pipeline_worker_heartbeats
        ORDER BY last_heartbeat_at DESC;
    """
    return read_query(query, "get_worker_cluster_heartbeat_ledger")


@st.cache_data(ttl=5)
def get_active_backlog_metrics() -> pd.DataFrame:
    """
    17. Backlog Backpressure Tracker: Measures the absolute pending queue depth 
    and captures the precise age of the oldest unresolved event record on disk [INDEX].
    """
    query = """
        SELECT 
            COUNT(*) AS pending_backlog_count,
            MIN(pes.event_time) AS oldest_pending_event_time,
            CURRENT_TIMESTAMP - MIN(pes.event_time) AS max_backlog_lag_age
        FROM pipeline_event_store pes
        LEFT JOIN event_processing ep ON pes.event_id = ep.event_id
        WHERE ep.status IS NULL OR ep.status IN ('PENDING', 'RETRY');
    """
    return read_query(query, "get_active_backlog_metrics")
@st.cache_data(ttl=5)
def get_event_processing_summary_metrics() -> pd.DataFrame:
    """
    4, 5 & 6. Event System Observability Loader: Calculates backlog metrics, 
    status stratifications, and transaction-safe failure rate percentages [INDEX].
    """
    query = """
        SELECT 
            COUNT(*) AS total_records,
            COUNT(*) FILTER (WHERE status = 'PROCESSED') AS processed,
            COUNT(*) FILTER (WHERE status = 'PROCESSING') AS processing,
            COUNT(*) FILTER (WHERE status IN ('PENDING', 'RETRY')) AS pending_backlog,
            COUNT(*) FILTER (WHERE status = 'FAILED') AS failed,
            ROUND(
                100.0 * COUNT(*) FILTER (WHERE status = 'FAILED') 
                / NULLIF(COUNT(*), 0), 
                2
            ) AS failure_rate_pct
        FROM event_processing;
    """
    return read_query(query, "get_event_processing_summary_metrics")


@st.cache_data(ttl=5)
def get_event_processing_status_breakdown() -> pd.DataFrame:
    """5. Grouping Loader: Groups processing records by status families [INDEX]."""
    query = """
        SELECT status, COUNT(*) AS total
        FROM event_processing
        GROUP BY status
        ORDER BY status ASC;
    """
    return read_query(query, "get_event_processing_status_breakdown")


@st.cache_data(ttl=5)
def get_worker_nodes_heartbeat_ledger() -> pd.DataFrame:
    """
    11 & 12. Worker Health Audit: Queries active worker heartbeats and computes 
    exact age intervals to identify stale cluster nodes cleanly [INDEX].
    """
    query = """
        SELECT worker_id, status, last_heartbeat_at,
               EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - last_heartbeat_at)) AS heartbeat_age_seconds,
               events_processed, errors_count
        FROM pipeline_worker_heartbeats
        ORDER BY last_heartbeat_at DESC;
    """
    return read_query(query, "get_worker_nodes_heartbeat_ledger")


@st.cache_data(ttl=5)
def get_detailed_event_lag_and_retry_metrics() -> pd.DataFrame:
    """
    7 & 8. Advanced Telemetry Loader: Computes historical retry activity totals 
    alongside average queue lag times and oldest pending landmarks [INDEX].
    """
    query = """
        SELECT 
            COALESCE(SUM(ep.attempt_count - 1), 0) AS total_retry_events,
            MIN(pes.event_time) AS oldest_pending_event_time,
            EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MIN(pes.event_time))) AS max_lag_seconds,
            EXTRACT(EPOCH FROM AVG(CURRENT_TIMESTAMP - pes.event_time)) AS avg_lag_seconds
        FROM pipeline_event_store pes
        JOIN event_processing ep ON pes.event_id = ep.event_id
        WHERE ep.status IN ('PENDING', 'RETRY', 'PROCESSING');
    """
    return read_query(query, "get_detailed_event_lag_and_retry_metrics")
@st.cache_data(ttl=5)
def get_unified_event_processing_telemetry() -> pd.DataFrame:
    """
    14, 17 & 21. Defensive Ingestion Metrics Loader: Collects all lifecycle counts 
    and handles empty system catalog tables safely without raising a ZeroDivisionError [INDEX].
    """
    query = """
        SELECT
            COUNT(*) AS total_records,
            COALESCE(COUNT(*) FILTER (WHERE status = 'PENDING'), 0) AS pending,
            COALESCE(COUNT(*) FILTER (WHERE status = 'PROCESSING'), 0) AS processing,
            COALESCE(COUNT(*) FILTER (WHERE status = 'PROCESSED'), 0) AS processed,
            COALESCE(COUNT(*) FILTER (WHERE status = 'RETRY'), 0) AS retry,
            COALESCE(COUNT(*) FILTER (WHERE status = 'FAILED'), 0) AS failed,
            -- Secure division-by-zero shield via NULLIF constraints [INDEX]
            ROUND(
                100.0 * COALESCE(COUNT(*) FILTER (WHERE status = 'FAILED'), 0) / 
                NULLIF(COUNT(*), 0), 
                2
            ) AS failure_rate_pct,
            COALESCE(
                COUNT(*) FILTER (WHERE status = 'PROCESSED') / 
                NULLIF(EXTRACT(EPOCH FROM SUM(processed_at - last_attempt_at) FILTER (WHERE status = 'PROCESSED')), 0),
                0.0
            ) AS processed_per_second
        FROM event_processing;
    """
    return read_query(query, "get_unified_event_processing_telemetry")
