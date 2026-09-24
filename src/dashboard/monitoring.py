import pandas as pd
import streamlit as st
from sqlalchemy import text
from src.database import engine
from src.dashboard.data import read_query

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
