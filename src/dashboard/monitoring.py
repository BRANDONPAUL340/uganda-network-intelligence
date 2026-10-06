
"""
Uganda Network Intelligence Platform — UI Monitoring Driver Layer
Performance-optimized data extraction drivers utilizing selective caching [INDEX].
"""
import sys
from pathlib import Path
import pandas as pd
import streamlit as st
from src.dashboard.data import read_query

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def get_pipeline_summary_metrics() -> dict:
    """Overview Metric Driver: Computes throughput aggregate statistics from disk."""
    try:
        runs_query = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as success,
                COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed
            FROM pipeline_runs;
        """
        runs_df = read_query(runs_query, "get_pipeline_runs_summary")
        
        incidents_query = """
            SELECT COUNT(*) as open_alerts 
            FROM pipeline_incidents 
            WHERE status != 'RESOLVED';
        """
        incidents_df = read_query(incidents_query, "get_active_incidents_count")
        
        total_runs = int(runs_df["total"].iloc[0]) if not runs_df.empty and pd.notna(runs_df["total"].iloc[0]) else 0
        success_runs = int(runs_df["success"].iloc[0]) if not runs_df.empty and pd.notna(runs_df["success"].iloc[0]) else 0
        failed_runs = int(runs_df["failed"].iloc[0]) if not runs_df.empty and pd.notna(runs_df["failed"].iloc[0]) else 0
        open_incidents = int(incidents_df["open_alerts"].iloc[0]) if not incidents_df.empty and pd.notna(incidents_df["open_alerts"].iloc[0]) else 0
        
        return {
            "status": "HEALTHY",
            "total_runs": total_runs,
            "success_runs": success_runs,
            "failed_runs": failed_runs,
            "open_incidents": open_incidents
        }
    except Exception as exc:
        print(f"🔴 Central analytics aggregation engine failure: {exc}")
        return {"status": "ERROR", "total_runs": 0, "success_runs": 0, "failed_runs": 0, "open_incidents": 0}


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
    """Step Trace Fetcher: Pulls sub-task items for a specific run_id using parameter bindings."""
    try:
        query = """
            SELECT step_id, step_name, status, started_at, completed_at
            FROM pipeline_steps
            WHERE run_id = :run_id
            ORDER BY started_at ASC;
        """
        return read_query(query, "get_pipeline_run_steps_trace", params={"run_id": run_id})
    except Exception as exc:
        print(f"🔴 Sub-step extraction driver failure for run_id {run_id}: {exc}")
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


def get_filtered_data_quality_results(status_filter: str = "All", run_id_filter: str = "All") -> pd.DataFrame:
    """Multi-Dimensional Grid Driver: Pulls detailed validation reports matching criteria parameters."""
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
                quality_result_id AS result_id,
                run_id,
                check_name,
                status,
                NULL AS measured_value,
                NULL AS threshold_value,
                checked_at AS evaluated_at
            FROM data_quality_results
            {where_clause}
            ORDER BY checked_at DESC
            LIMIT 100;
        """
        return read_query(query, "get_filtered_data_quality_results", params=params)
    except Exception as exc:
        print(f"🔴 Data quality filter log pipeline extraction failure: {exc}")
        return pd.DataFrame()


def get_incidents_summary_metrics() -> dict:
    """Metrics Driver: Computes open, closed, and high-severity incident counts."""
    try:
        query = """
            SELECT 
                COUNT(*) as total_alerts,
                COUNT(CASE WHEN status != 'RESOLVED' THEN 1 END) as open_alerts,
                COUNT(CASE WHEN status = 'RESOLVED' THEN 1 END) as resolved_alerts,
                COUNT(CASE WHEN severity IN ('CRITICAL', 'HIGH') AND status != 'RESOLVED' THEN 1 END) as severe_alerts
            FROM pipeline_incidents;
        """
        df = read_query(query, "get_incidents_summary_metrics")
        
        total = int(df["total_alerts"].iloc[0]) if not df.empty and pd.notna(df["total_alerts"].iloc[0]) else 0
        open_count = int(df["open_alerts"].iloc[0]) if not df.empty and pd.notna(df["open_alerts"].iloc[0]) else 0
        resolved = int(df["resolved_alerts"].iloc[0]) if not df.empty and pd.notna(df["resolved_alerts"].iloc[0]) else 0
        severe = int(df["severe_alerts"].iloc[0]) if not df.empty and pd.notna(df["severe_alerts"].iloc[0]) else 0
        
        return {"status": "HEALTHY", "total": total, "open": open_count, "resolved": resolved, "severe": severe}
    except Exception as exc:
        print(f"🔴 Incidents summary matrix calculation failure: {exc}")
        return {"status": "ERROR", "total": 0, "open": 0, "resolved": 0, "severe": 0}


def get_filtered_incidents_logs(status_filter: str = "All", severity_filter: str = "All") -> pd.DataFrame:
    """Parameterized Log Fetcher: Pulls incident reports matching selection criteria safely."""
    try:
        params = {}
        conditions = []

        if status_filter != "All":
            if status_filter == "OPEN":
                conditions.append("status != 'RESOLVED'")
            else:
                conditions.append("status = :status")
                params["status"] = status_filter

        if severity_filter != "All":
            conditions.append("severity = :severity")
            params["severity"] = severity_filter

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT
                incident_id,
                run_id,
                check_name AS title,
                message AS description,
                severity,
                status,
                created_at,
                resolved_at
            FROM pipeline_incidents
            {where_clause}
            ORDER BY created_at DESC
            LIMIT 100;
        """

        return read_query(query, "get_filtered_incidents_logs", params=params)

    except Exception as exc:
        print(f"Filtered incidents ledger retrieval failure: {exc}")
        return pd.DataFrame()


def get_event_workers_summary_metrics() -> dict:
    """Build event/worker-style metrics from the current pipeline run registry."""
    try:
        query = """
            SELECT
                COUNT(*) AS total_events,
                COUNT(*) FILTER (WHERE status IN ('SUCCESS', 'COMPLETED')) AS success_events,
                COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_events,
                COALESCE(SUM(COALESCE(records_processed, 0)), 0) AS total_processed
            FROM pipeline_runs;
        """

        df = read_query(query, "get_event_workers_summary_metrics")

        if df.empty:
            return {
                "status": "HEALTHY",
                "total": 0,
                "success": 0,
                "failed": 0,
                "retries": 0,
            }

        row = df.iloc[0]

        return {
            "status": "HEALTHY",
            "total": int(row["total_events"] or 0),
            "success": int(row["success_events"] or 0),
            "failed": int(row["failed_events"] or 0),
            "retries": 0,
        }

    except Exception:
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
    """Provides the Events page ledger using the current pipeline run registry."""
    try:
        params = {}
        conditions = []

        if type_filter != "All":
            conditions.append("pipeline_name = :event_type")
            params["event_type"] = type_filter

        if status_filter != "All":
            conditions.append("status = :status")
            params["status"] = status_filter

        where_clause = (
            f"WHERE {' AND '.join(conditions)}"
            if conditions
            else ""
        )

        query = f"""
            SELECT
                run_id AS event_id,
                pipeline_name AS event_type,
                run_id,
                'pipeline' AS producer,
                started_at AS created_at,
                status,
                0 AS retry_count,
                completed_at AS processed_at
            FROM pipeline_runs
            {where_clause}
            ORDER BY started_at DESC
            LIMIT 100;
        """

        return read_query(
            query,
            "get_filtered_events_ledger",
            params=params,
        )

    except Exception:
        return pd.DataFrame(
            columns=[
                "event_id",
                "event_type",
                "run_id",
                "producer",
                "created_at",
                "status",
                "retry_count",
                "processed_at",
            ]
        )


def get_events_distribution_by_type() -> pd.DataFrame:
    """Returns pipeline execution frequency by pipeline name."""
    try:
        query = """
            SELECT
                pipeline_name AS event_type,
                COUNT(*) AS total_events
            FROM pipeline_runs
            GROUP BY pipeline_name
            ORDER BY total_events DESC;
        """

        return read_query(
            query,
            "get_events_distribution_by_type",
        )

    except Exception:
        return pd.DataFrame(
            columns=["event_type", "total_events"]
        )


def get_lineage_summary_metrics() -> dict:
    """Metrics Driver: Computes total tracking pathways and cumulative volume throughput metrics safely."""
    try:
        query = """
            SELECT
                COUNT(*) as total_records,
                COUNT(DISTINCT target_table) as unique_targets,
                SUM(COALESCE(records_processed, 0)) as cumulative_rows
            FROM pipeline_lineage;
        """

        df = read_query(query, "get_lineage_summary_metrics")

        records = (
            int(df["total_records"].iloc[0])
            if not df.empty and pd.notna(df["total_records"].iloc[0])
            else 0
        )

        targets = (
            int(df["unique_targets"].iloc[0])
            if not df.empty and pd.notna(df["unique_targets"].iloc[0])
            else 0
        )

        total_rows = (
            int(df["cumulative_rows"].iloc[0])
            if not df.empty and pd.notna(df["cumulative_rows"].iloc[0])
            else 0
        )

        return {
            "status": "HEALTHY",
            "records": records,
            "targets": targets,
            "cumulative_rows": total_rows,
        }

    except Exception as exc:
        print(f"Dataset lineage aggregate compiler failure: {exc}")
        return {
            "status": "ERROR",
            "records": 0,
            "targets": 0,
            "cumulative_rows": 0,
        }


def get_filtered_pipeline_lineage_logs(
    run_id_filter: str = "All",
) -> pd.DataFrame:
    """18. Verified Lineage Log Fetcher: Restricts targets to confirmed database columns cleanly."""
    try:
        params = {}
        where_clause = ""

        if run_id_filter != "All":
            where_clause = "WHERE run_id = :run_id"
            params["run_id"] = int(run_id_filter.replace("RUN-", ""))

        query = f"""
            SELECT
                lineage_id,
                run_id,
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
        print(f"Data lineage trace pipeline extraction driver failure: {exc}")
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
    """Cached Incident Categories: Caches categorical distributions safely for 30 seconds."""
    try:
        query = """
            SELECT
                severity,
                COUNT(*) as total_incidents
            FROM pipeline_incidents
            GROUP BY severity
            ORDER BY total_incidents DESC;
        """

        return read_query(
            query,
            "get_incidents_severity_distribution",
        )

    except Exception as exc:
        print(f"Incident classification cached bar aggregator crash: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=30)

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
                check_value,
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
                check_value,
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