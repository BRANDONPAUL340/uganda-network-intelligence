
import sys
from pathlib import Path
import pandas as pd
import streamlit as st
from src.dashboard.data import read_query

from sqlalchemy import text
from src.database import engine

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def get_pipeline_summary_metrics():
    """
    Return high-level pipeline and incident metrics using only
    tables and columns that exist in the current PostgreSQL schema.
    """
    try:
        with engine.connect() as connection:
            pipeline_result = connection.execute(
                text("""
                    SELECT
                        COUNT(*) AS total_runs,
                        COUNT(*) FILTER (WHERE status = 'SUCCESS') AS success_runs,
                        COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_runs,
                        COUNT(*) FILTER (WHERE status = 'RUNNING') AS running_runs
                    FROM pipeline_runs
                """)
            ).mappings().one()

            incident_result = connection.execute(
                text("""
                    SELECT
                        COUNT(*) AS total_incidents,
                        COUNT(*) FILTER (
                            WHERE UPPER(status) != 'RESOLVED'
                        ) AS open_incidents
                    FROM incidents
                """)
            ).mappings().one()

        return {
            "status": "HEALTHY",
            "total_runs": int(pipeline_result["total_runs"] or 0),
            "success_runs": int(pipeline_result["success_runs"] or 0),
            "failed_runs": int(pipeline_result["failed_runs"] or 0),
            "running_runs": int(pipeline_result["running_runs"] or 0),
            "total_incidents": int(incident_result["total_incidents"] or 0),
            "open_incidents": int(incident_result["open_incidents"] or 0),
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "total_runs": 0,
            "success_runs": 0,
            "failed_runs": 0,
            "running_runs": 0,
            "total_incidents": 0,
            "open_incidents": 0,
            "error": str(exc),
        }

def get_recent_pipeline_logs(limit: int = 5) -> pd.DataFrame:
    """Pulls a lightweight subset of recent pipeline executions for the Overview landing."""
    try:
        query = f"""
            SELECT 
                run_id, 
                pipeline_name, 
                current_stage, 
                status, 
                started_at,
                ROUND(EXTRACT(EPOCH FROM (COALESCE(completed_at, CURRENT_TIMESTAMP) - started_at))) AS duration_seconds
            FROM pipeline_runs
            ORDER BY started_at DESC
            LIMIT {limit};
        """
        return read_query(query, "get_recent_pipeline_logs")
    except Exception as exc:
        print(f"🔴 Log extraction driver failure: {exc}")
        return pd.DataFrame()


def get_filtered_pipeline_runs(status_filter: str = "All", run_id_filter: str = "All") -> pd.DataFrame:
    """Filtered Runs Fetcher: Executes filtering and bounding directly within PostgreSQL."""
    try:
        params = {}
        conditions = []
        if status_filter != "All":
            conditions.append("status = :status")
            params["status"] = status_filter
        if run_id_filter != "All":
            conditions.append("run_id = :run_id")
            params["run_id"] = int(run_id_filter.replace("RUN-", ""))
            
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            
        query = f"""
            SELECT 
                run_id,
                pipeline_name,
                current_stage,
                status,
                started_at,
                completed_at,
                ROUND(EXTRACT(EPOCH FROM (COALESCE(completed_at, CURRENT_TIMESTAMP) - started_at))) AS duration_seconds,
                CASE WHEN completed_at IS NULL THEN 'RUNNING' ELSE 'COMPLETED' END as temporal_state
            FROM pipeline_runs
            {where_clause}
            ORDER BY started_at DESC
            LIMIT 100;
        """
        return read_query(query, "get_filtered_pipeline_runs", params=params)
    except Exception as exc:
        print(f"🔴 Filtered execution logs driver crash: {exc}")
        return pd.DataFrame()


def get_pipeline_run_steps_trace(run_id: int) -> pd.DataFrame:
    """
    Fetch granular processing stages for a specific pipeline run
    using the authoritative pipeline_stage_runs schema.
    """
    try:
        query = """
            SELECT
                stage_run_id,
                run_id,
                stage_name,
                status,
                started_at,
                completed_at,
                records_read,
                records_inserted,
                records_rejected,
                records_skipped,
                duration_seconds,
                error_message
            FROM pipeline_stage_runs
            WHERE run_id = :run_id
            ORDER BY started_at ASC;
        """

        return read_query(
            query,
            "get_pipeline_run_steps_trace",
            params={"run_id": run_id},
        )

    except Exception as exc:
        print(
            f"Sub-step extraction driver failure for run_id {run_id}: {exc}"
        )
        return pd.DataFrame()

def get_data_quality_summary_metrics() -> dict:
    """Metric Driver: Computes comprehensive pass, warning, and failure aggregates from disk."""
    try:
        query = """
            SELECT 
                COUNT(CASE WHEN status = 'PASS' THEN 1 END) as pass_count,
                COUNT(CASE WHEN status = 'WARN' THEN 1 END) as warn_count,
                COUNT(CASE WHEN status = 'FAIL' THEN 1 END) as fail_count
            FROM data_quality_results;
        """
        df = read_query(query, "get_data_quality_summary_metrics")
        
        passes = int(df["pass_count"].iloc[0]) if not df.empty and pd.notna(df["pass_count"].iloc[0]) else 0
        warnings = int(df["warn_count"].iloc[0]) if not df.empty and pd.notna(df["warn_count"].iloc[0]) else 0
        failures = int(df["fail_count"].iloc[0]) if not df.empty and pd.notna(df["fail_count"].iloc[0]) else 0
        
        return {"status": "HEALTHY", "pass": passes, "warn": warnings, "fail": failures}
    except Exception as exc:
        print(f"🔴 Data quality summary aggregation driver crash: {exc}")
        return {"status": "ERROR", "pass": 0, "warn": 0, "fail": 0}


def get_filtered_data_quality_results(
    status_filter: str = "All",
    run_id_filter: str = "All",
) -> pd.DataFrame:
    """
    Fetch data-quality validation results using the authoritative
    data_quality_results schema.
    """
    try:
        params = {}
        conditions = []

        if status_filter != "All":
            conditions.append("status = :status")
            params["status"] = status_filter

        if run_id_filter != "All":
            conditions.append("run_id = :run_id")
            params["run_id"] = int(run_id_filter.replace("RUN-", ""))

        where_clause = (
            f"WHERE {' AND '.join(conditions)}"
            if conditions
            else ""
        )

        query = f"""
            SELECT
                quality_result_id,
                run_id,
                table_name,
                check_name,
                check_type,
                status,
                records_checked,
                records_failed,
                failure_rate_pct,
                details,
                checked_at,
                error_message,
                severity
            FROM data_quality_results
            {where_clause}
            ORDER BY checked_at DESC
            LIMIT 100;
        """

        return read_query(
            query,
            "get_filtered_data_quality_results",
            params=params,
        )

    except Exception as exc:
        print(
            f"Data quality filter log pipeline extraction failure: {exc}"
        )
        return pd.DataFrame()


def get_incidents_summary_metrics() -> dict:
    """
    Return incident summary metrics using the authoritative
    incidents schema.
    """
    try:
        query = """
            SELECT
                COUNT(*) AS total_incidents,
                COUNT(*) FILTER (
                    WHERE UPPER(status) != 'RESOLVED'
                ) AS open_incidents,
                COUNT(*) FILTER (
                    WHERE UPPER(severity) IN ('CRITICAL', 'HIGH')
                ) AS critical_high_incidents,
                COUNT(*) FILTER (
                    WHERE UPPER(status) = 'RESOLVED'
                ) AS resolved_incidents
            FROM incidents;
        """

        df = read_query(
            query,
            "get_incidents_summary_metrics",
        )

        if df.empty:
            return {
                "total_incidents": 0,
                "open_incidents": 0,
                "critical_high_incidents": 0,
                "resolved_incidents": 0,
            }

        row = df.iloc[0]

        return {
            "total_incidents": int(row["total_incidents"] or 0),
            "open_incidents": int(row["open_incidents"] or 0),
            "critical_high_incidents": int(
                row["critical_high_incidents"] or 0
            ),
            "resolved_incidents": int(
                row["resolved_incidents"] or 0
            ),
        }

    except Exception as exc:
        print(f"Incident summary extraction failure: {exc}")
        return {
            "total_incidents": 0,
            "open_incidents": 0,
            "critical_high_incidents": 0,
            "resolved_incidents": 0,
            "error": str(exc),
        }
def get_filtered_incidents_logs(
    status_filter: str = "All",
    severity_filter: str = "All",
) -> pd.DataFrame:
    """
    Fetch incident records using the authoritative incidents schema.
    """
    try:
        params = {}
        conditions = []

        if status_filter != "All":
            conditions.append("UPPER(status) = :status")
            params["status"] = status_filter.upper()

        if severity_filter != "All":
            conditions.append("UPPER(severity) = :severity")
            params["severity"] = severity_filter.upper()

        where_clause = (
            f"WHERE {' AND '.join(conditions)}"
            if conditions
            else ""
        )

        query = f"""
            SELECT
                incident_id,
                site_id,
                equipment_id,
                incident_type,
                severity,
                status,
                start_time,
                end_time,
                description
            FROM incidents
            {where_clause}
            ORDER BY start_time DESC
            LIMIT 100;
        """

        return read_query(
            query,
            "get_filtered_incidents_logs",
            params=params,
        )

    except Exception as exc:
        print(
            f"Incident log extraction failure: {exc}"
        )
        return pd.DataFrame()

def get_event_workers_summary_metrics() -> dict:
    """Computes comprehensive aggregates for emitted events and backoff retries safely from disk."""
    try:
        store_query = "SELECT COUNT(*) as total_evts FROM pipeline_event_store;"

        proc_query = """
            SELECT
                COUNT(CASE WHEN status = 'PROCESSED' THEN 1 END) as success_evts,
                COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_evts,
                SUM(COALESCE(retry_count, 0)) as total_retries
            FROM event_processing;
        """

        store_df = read_query(store_query, "get_total_events_count")
        proc_df = read_query(proc_query, "get_processing_worker_aggregates")

        total = (
            int(store_df["total_evts"].iloc[0])
            if not store_df.empty and pd.notna(store_df["total_evts"].iloc[0])
            else 0
        )

        success = (
            int(proc_df["success_evts"].iloc[0])
            if not proc_df.empty and pd.notna(proc_df["success_evts"].iloc[0])
            else 0
        )

        failed = (
            int(proc_df["failed_evts"].iloc[0])
            if not proc_df.empty and pd.notna(proc_df["failed_evts"].iloc[0])
            else 0
        )

        retries = (
            int(proc_df["total_retries"].iloc[0])
            if not proc_df.empty and pd.notna(proc_df["total_retries"].iloc[0])
            else 0
        )

        return {
            "status": "HEALTHY",
            "total": total,
            "success": success,
            "failed": failed,
            "retries": retries,
        }

    except Exception as exc:
        print(f"Event worker metrics summary compilation crash: {exc}")
        return {
            "status": "ERROR",
            "total": 0,
            "success": 0,
            "failed": 0,
            "retries": 0,
        }


def get_filtered_events_ledger(
    type_filter: str = "All",
    status_filter: str = "All",
) -> pd.DataFrame:
    """Combines append-only log maps and worker state registers to filter streaming queues safely."""
    try:
        params = {}
        conditions = []

        if type_filter != "All":
            conditions.append("s.event_type = :event_type")
            params["event_type"] = type_filter

        if status_filter != "All":
            conditions.append("p.status = :status")
            params["status"] = status_filter

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT
                s.event_id,
                s.event_type,
                s.run_id,
                s.producer,
                s.created_at,
                COALESCE(p.status, 'PENDING') as status,
                COALESCE(p.retry_count, 0) as retry_count,
                p.processed_at
            FROM pipeline_event_store s
            LEFT JOIN event_processing p ON s.event_id = p.event_id
            {where_clause}
            ORDER BY s.created_at DESC
            LIMIT 100;
        """

        return read_query(query, "get_filtered_events_ledger", params=params)

    except Exception as exc:
        print(f"Filtered event queue extraction crash: {exc}")
        return pd.DataFrame()


def get_lineage_summary_metrics() -> dict:
    """
    Return lineage summary metrics using the authoritative
    pipeline_lineage schema.
    """
    try:
        query = """
            SELECT
                COUNT(*) AS total_records,
                COUNT(DISTINCT target_table) AS unique_targets,
                COALESCE(SUM(records_processed), 0) AS cumulative_rows
            FROM pipeline_lineage;
        """

        df = read_query(
            query,
            "get_lineage_summary_metrics",
        )

        if df.empty:
            return {
                "total_records": 0,
                "unique_targets": 0,
                "cumulative_rows": 0,
            }

        row = df.iloc[0]

        return {
            "total_records": int(row["total_records"] or 0),
            "unique_targets": int(row["unique_targets"] or 0),
            "cumulative_rows": int(row["cumulative_rows"] or 0),
        }

    except Exception as exc:
        print(f"Lineage summary extraction failure: {exc}")
        return {
            "total_records": 0,
            "unique_targets": 0,
            "cumulative_rows": 0,
        }


def get_filtered_pipeline_lineage_logs(
    run_id_filter: str = "All",
) -> pd.DataFrame:
    """
    Fetch pipeline lineage records using the authoritative
    pipeline_lineage schema.
    """
    try:
        params = {}
        conditions = []

        if run_id_filter != "All":
            conditions.append("run_id = :run_id")
            params["run_id"] = int(
                run_id_filter.replace("RUN-", "")
            )

        where_clause = (
            f"WHERE {' AND '.join(conditions)}"
            if conditions
            else ""
        )

        query = f"""
            SELECT
                lineage_id,
                run_id,
                source_table,
                target_table,
                records_processed,
                created_at
            FROM pipeline_lineage
            {where_clause}
            ORDER BY created_at DESC
            LIMIT 100;
        """

        return read_query(
            query,
            "get_filtered_pipeline_lineage_logs",
            params=params,
        )

    except Exception as exc:
        print(
            f"Pipeline lineage extraction failure: {exc}"
        )
        return pd.DataFrame()

# ==============================================================================
# OPTIMIZED TIME-SERIES CACHING LAYERS (Day 238) [INDEX]
# ==============================================================================

@st.cache_data(ttl=30)
def get_pipeline_runs_time_series() -> pd.DataFrame:
    """Short-TTL Cached Trend Aggregator: Enforces a strict 30-second cache threshold."""
    try:
        query = """
            SELECT
                DATE(started_at) as run_date,
                COUNT(*) as total_runs,
                COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as success_runs,
                COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_runs
            FROM pipeline_runs
            GROUP BY DATE(started_at)
            ORDER BY run_date ASC;
        """

        return read_query(query, "get_pipeline_runs_time_series")

    except Exception as exc:
        print(f"Cached time-series trend database driver crash: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=30)
def get_data_quality_trends() -> pd.DataFrame:
    """Short-TTL Cached Quality Trend Aggregator."""
    try:
        query = """
            SELECT
                DATE(checked_at) as eval_date,
                COUNT(CASE WHEN status = 'PASS' THEN 1 END) as pass_count,
                COUNT(CASE WHEN status = 'WARN' THEN 1 END) as warn_count,
                COUNT(CASE WHEN status = 'FAIL' THEN 1 END) as fail_count
            FROM data_quality_results
            GROUP BY DATE(checked_at)
            ORDER BY eval_date ASC;
        """

        return read_query(query, "get_data_quality_trends")

    except Exception as exc:
        print(f"Data quality cached trend line aggregation crash: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=30)
def get_incidents_severity_distribution() -> pd.DataFrame:
    """
    Return incident counts grouped by severity.
    """
    try:
        query = """
            SELECT
                UPPER(severity) AS severity,
                COUNT(*) AS incident_count
            FROM incidents
            GROUP BY UPPER(severity)
            ORDER BY
                CASE UPPER(severity)
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                    ELSE 5
                END;
        """

        return read_query(
            query,
            "get_incidents_severity_distribution",
        )

    except Exception as exc:
        print(
            f"Incident severity distribution extraction failure: {exc}"
        )
        return pd.DataFrame()


@st.cache_data(ttl=30)
def get_events_distribution_by_type() -> pd.DataFrame:
    """Cached Event Frequencies: Reduces transactional throughput overhead."""
    try:
        query = """
            SELECT
                event_type,
                COUNT(*) as total_events
            FROM pipeline_event_store
            GROUP BY event_type
            ORDER BY total_events DESC;
        """

        return read_query(
            query,
            "get_events_distribution_by_type",
        )

    except Exception as exc:
        print(f"Event types cached stream distribution compiler crash: {exc}")
        return pd.DataFrame()
def get_open_alerts() -> pd.DataFrame:
    try:
        query = """
            SELECT
                incident_id,
                run_id,
                check_name,
                severity,
                status,
                message,
                created_at,
                resolved_at
            FROM pipeline_incidents
            WHERE status = 'OPEN'
            ORDER BY created_at DESC;
        """
        return read_query(query, "get_open_alerts")
    except Exception as exc:
        print(f"Open alerts retrieval failure: {exc}")
        return pd.DataFrame()


def get_recent_runs(limit: int = 10) -> pd.DataFrame:
    try:
        query = """
            SELECT
                run_id,
                pipeline_name,
                started_at,
                completed_at,
                status,
                current_stage,
                records_processed,
                duration_seconds
            FROM pipeline_runs
            ORDER BY started_at DESC
            LIMIT :limit;
        """
        return read_query(query, "get_recent_runs", params={"limit": limit})
    except Exception as exc:
        print(f"Recent runs retrieval failure: {exc}")
        return pd.DataFrame()


def get_failed_runs(limit: int = 100) -> pd.DataFrame:
    try:
        query = """
            SELECT
                run_id,
                pipeline_name,
                started_at,
                completed_at,
                status,
                current_stage,
                records_processed,
                error_message,
                duration_seconds
            FROM pipeline_runs
            WHERE status = 'FAILED'
            ORDER BY started_at DESC
            LIMIT :limit;
        """
        return read_query(query, "get_failed_runs", params={"limit": limit})
    except Exception as exc:
        print(f"Failed runs retrieval failure: {exc}")
        return pd.DataFrame()


def get_failed_steps(limit: int = 100) -> pd.DataFrame:
    try:
        query = """
            SELECT
                step_id,
                run_id,
                step_name,
                status,
                started_at,
                completed_at,
                records_processed,
                error_message
            FROM pipeline_steps
            WHERE status = 'FAILED'
            ORDER BY started_at DESC
            LIMIT :limit;
        """
        return read_query(query, "get_failed_steps", params={"limit": limit})
    except Exception as exc:
        print(f"Failed steps retrieval failure: {exc}")
        return pd.DataFrame()


def get_run_summary() -> pd.DataFrame:
    try:
        query = """
            SELECT
                COUNT(*) AS total_runs,
                COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) AS successful_runs,
                COUNT(CASE WHEN status = 'FAILED' THEN 1 END) AS failed_runs,
                COUNT(CASE WHEN status = 'RUNNING' THEN 1 END) AS running_runs
            FROM pipeline_runs;
        """
        return read_query(query, "get_run_summary")
    except Exception as exc:
        print(f"Run summary retrieval failure: {exc}")
        return pd.DataFrame()


def get_last_successful_run() -> pd.DataFrame:
    try:
        query = """
            SELECT
                run_id,
                pipeline_name,
                started_at,
                completed_at,
                status,
                current_stage,
                records_processed,
                duration_seconds
            FROM pipeline_runs
            WHERE status = 'SUCCESS'
            ORDER BY completed_at DESC NULLS LAST
            LIMIT 1;
        """
        return read_query(query, "get_last_successful_run")
    except Exception as exc:
        print(f"Last successful run retrieval failure: {exc}")
        return pd.DataFrame()


def get_available_runs() -> pd.DataFrame:
    try:
        query = """
            SELECT
                run_id,
                pipeline_name,
                status,
                started_at
            FROM pipeline_runs
            ORDER BY started_at DESC;
        """
        return read_query(query, "get_available_runs")
    except Exception as exc:
        print(f"Available runs retrieval failure: {exc}")
        return pd.DataFrame()


def get_run_steps(run_id: int) -> pd.DataFrame:
    try:
        query = """
            SELECT
                step_id,
                run_id,
                step_name,
                status,
                started_at,
                completed_at,
                records_processed,
                error_message
            FROM pipeline_steps
            WHERE run_id = :run_id
            ORDER BY started_at ASC;
        """
        return read_query(query, "get_run_steps", params={"run_id": run_id})
    except Exception as exc:
        print(f"Run steps retrieval failure: {exc}")
        return pd.DataFrame()


def get_run_incidents(run_id: int) -> pd.DataFrame:
    try:
        query = """
            SELECT
                incident_id,
                run_id,
                check_name,
                severity,
                status,
                message,
                created_at,
                resolved_at
            FROM pipeline_incidents
            WHERE run_id = :run_id
            ORDER BY created_at DESC;
        """
        return read_query(query, "get_run_incidents", params={"run_id": run_id})
    except Exception as exc:
        print(f"Run incidents retrieval failure: {exc}")
        return pd.DataFrame()


def get_quality_summary() -> pd.DataFrame:
    try:
        query = """
            SELECT
                COUNT(*) AS total_checks,
                COUNT(CASE WHEN status = 'PASS' THEN 1 END) AS pass_count,
                COUNT(CASE WHEN status = 'WARN' THEN 1 END) AS warn_count,
                COUNT(CASE WHEN status = 'FAIL' THEN 1 END) AS fail_count
            FROM data_quality_results;
        """
        return read_query(query, "get_quality_summary")
    except Exception as exc:
        print(f"Quality summary retrieval failure: {exc}")
        return pd.DataFrame()


def get_quality_failure_rates() -> pd.DataFrame:
    try:
        query = """
            SELECT
                check_name,
                COUNT(*) AS total_checks,
                COUNT(CASE WHEN status = 'FAIL' THEN 1 END) AS failed_checks,
                ROUND(
                    100.0 * COUNT(CASE WHEN status = 'FAIL' THEN 1 END)
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS failure_rate_pct
            FROM data_quality_results
            GROUP BY check_name
            ORDER BY failure_rate_pct DESC NULLS LAST;
        """
        return read_query(query, "get_quality_failure_rates")
    except Exception as exc:
        print(f"Quality failure rates retrieval failure: {exc}")
        return pd.DataFrame()


def get_latest_quality_status() -> pd.DataFrame:
    try:
        query = """
            SELECT DISTINCT ON (check_name)
                quality_id,
                run_id,
                check_name,
                status,
                records_checked,
                failed_records,
                measured_value,
                message,
                checked_at
            FROM data_quality_results
            ORDER BY check_name, checked_at DESC;
        """
        return read_query(query, "get_latest_quality_status")
    except Exception as exc:
        print(f"Latest quality status retrieval failure: {exc}")
        return pd.DataFrame()


def get_quality_history() -> pd.DataFrame:
    try:
        query = """
            SELECT
                quality_id,
                run_id,
                check_name,
                status,
                records_checked,
                failed_records,
                measured_value,
                message,
                checked_at
            FROM data_quality_results
            ORDER BY checked_at DESC;
        """
        return read_query(query, "get_quality_history")
    except Exception as exc:
        print(f"Quality history retrieval failure: {exc}")
        return pd.DataFrame()


def get_unified_event_processing_telemetry() -> pd.DataFrame:
    try:
        query = """
            SELECT
                COUNT(*) AS total_records,
                COUNT(CASE WHEN status = 'PROCESSED' THEN 1 END) AS processed_records,
                COUNT(CASE WHEN status = 'FAILED' THEN 1 END) AS failed_records,
                CASE
                    WHEN COUNT(*) = 0 THEN NULL
                    ELSE ROUND(
                        100.0 * COUNT(CASE WHEN status = 'FAILED' THEN 1 END)
                        / COUNT(*),
                        2
                    )
                END AS failure_rate_pct,
                COALESCE(SUM(attempt_count), 0) AS total_attempts
            FROM event_processing;
        """
        return read_query(query, "get_unified_event_processing_telemetry")
    except Exception as exc:
        print(f"Event processing telemetry retrieval failure: {exc}")
        return pd.DataFrame()


def get_worker_nodes_heartbeat_ledger() -> pd.DataFrame:
    try:
        query = """
            SELECT
                worker_id,
                status,
                last_heartbeat_at,
                events_processed,
                errors_count
            FROM pipeline_worker_heartbeats
            ORDER BY last_heartbeat_at DESC;
        """
        return read_query(query, "get_worker_nodes_heartbeat_ledger")
    except Exception as exc:
        print(f"Worker heartbeat ledger retrieval failure: {exc}")
        return pd.DataFrame()