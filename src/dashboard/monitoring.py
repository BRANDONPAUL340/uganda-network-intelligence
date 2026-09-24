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
def get_run_steps(run_id: int) -> pd.DataFrame:
    """
    7. Parameterized Sub-Stage Finder: Retrieves granular task execution logs
    filtered exclusively by the operator's chosen Parent Run ID [INDEX].
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
def get_run_details(run_id: int) -> pd.DataFrame:
    """
    10. Parameterized Run Details Loader: Retrieves top-level batch metadata
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
