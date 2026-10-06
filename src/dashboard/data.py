"""
Uganda Network Intelligence Platform - Data Access Layer
Centralizes connection parameters and dashboard data access.
"""

import os
import sys

import pandas as pd
from sqlalchemy import create_engine, text


ENVIRONMENT = os.getenv("ENVIRONMENT", "DEVELOPMENT").upper().strip()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("FATAL CONFIGURATION ERROR: DATABASE_URL environment parameter is missing.")
    print("Please execute 'set DATABASE_URL=...' before starting the application.")
    sys.exit(1)

if ENVIRONMENT == "TEST" and "test" not in DATABASE_URL.lower():
    print(
        "SECURITY FAULT: ENVIRONMENT is TEST but DATABASE_URL "
        f"points to a non-test target: [{DATABASE_URL}]"
    )
    sys.exit(1)


engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)


def read_query(
    query_string: str,
    query_name: str,
    params: dict = None,
) -> pd.DataFrame:
    """Execute a read-only dashboard query and return a DataFrame."""
    try:
        bind_parameters = params if params is not None else {}

        with engine.connect() as connection:
            return pd.read_sql(
                sql=text(query_string),
                con=connection,
                params=bind_parameters,
            )

    except Exception as exc:
        print(
            f"Relational access layer error on query "
            f"[{query_name}]: {exc}"
        )
        return pd.DataFrame()


def _safe_dataframe(df) -> pd.DataFrame:
    """Normalize failed/None query results to an empty DataFrame."""
    if isinstance(df, pd.DataFrame):
        return df
    return pd.DataFrame()


def get_pipeline_kpis() -> pd.DataFrame:
    """Return aggregate pipeline execution KPIs."""
    query = """
        SELECT
            COUNT(*) AS total_runs,
            COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful_runs,
            COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_runs,
            COUNT(*) FILTER (WHERE status = 'RUNNING') AS running_runs
        FROM pipeline_runs;
    """

    return _safe_dataframe(
        read_query(query, "get_pipeline_kpis")
    )


def get_current_health() -> pd.DataFrame:
    """Return current network health status distribution."""
    query = """
        SELECT
            health_status,
            COUNT(*) AS record_count
        FROM silver_network_health
        GROUP BY health_status
        ORDER BY record_count DESC;
    """

    return _safe_dataframe(
        read_query(query, "get_current_health")
    )


def get_daily_health() -> pd.DataFrame:
    """Return daily network health status counts."""
    query = """
        SELECT
            DATE(inserted_at) AS health_date,
            health_status,
            COUNT(*) AS record_count
        FROM silver_network_health
        GROUP BY DATE(inserted_at), health_status
        ORDER BY health_date ASC;
    """

    return _safe_dataframe(
        read_query(query, "get_daily_health")
    )


def get_stage_summary() -> pd.DataFrame:
    """Return pipeline execution counts grouped by current stage."""
    query = """
        SELECT
            current_stage,
            COUNT(*) AS run_count,
            COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful_runs,
            COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_runs,
            COUNT(*) FILTER (WHERE status = 'RUNNING') AS running_runs
        FROM pipeline_runs
        GROUP BY current_stage
        ORDER BY run_count DESC;
    """

    return _safe_dataframe(
        read_query(query, "get_stage_summary")
    )


def get_site_performance(
    region: str = None,
    district: str = None,
    start_date: str = None,
    end_date: str = None,
) -> pd.DataFrame:
    """Return aggregated network performance by site."""
    try:
        conditions = []
        params = {}

        if region:
            conditions.append("region = :region")
            params["region"] = region

        if district:
            conditions.append("district = :district")
            params["district"] = district

        if start_date:
            conditions.append("measured_at >= :start_date")
            params["start_date"] = start_date

        if end_date:
            conditions.append(
                "measured_at < CAST(:end_date AS DATE) + INTERVAL '1 day'"
            )
            params["end_date"] = end_date

        where_clause = ""

        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        query = f"""
            SELECT
                site_id,
                site_name,
                region,
                district,
                site_type,
                COUNT(*) AS measurement_count,
                AVG(traffic_mb) AS avg_traffic_mb,
                AVG(latency_ms) AS avg_latency_ms,
                AVG(packet_loss_pct) AS avg_packet_loss_pct,
                AVG(availability_pct) AS avg_availability_pct
            FROM silver_measurements
            {where_clause}
            GROUP BY
                site_id,
                site_name,
                region,
                district,
                site_type
            ORDER BY site_name ASC;
        """

        return _safe_dataframe(
            read_query(
                query,
                "get_site_performance",
                params=params,
            )
        )

    except Exception as exc:
        print(f"Site performance query failure: {exc}")
        return pd.DataFrame()


def get_network_summary() -> pd.DataFrame:
    """Return aggregate network measurement statistics."""
    query = """
        SELECT
            COUNT(DISTINCT site_id) AS total_sites,
            COUNT(*) AS total_measurements,
            AVG(traffic_mb) AS avg_traffic_mb,
            AVG(latency_ms) AS avg_latency_ms,
            AVG(packet_loss_pct) AS avg_packet_loss_pct,
            AVG(availability_pct) AS avg_availability_pct
        FROM silver_measurements;
    """

    return _safe_dataframe(
        read_query(query, "get_network_summary")
    )
def check_database_connection() -> bool:
    """Return True when the configured database connection is reachable."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        print(f"Database connectivity check failed: {exc}")
        return False