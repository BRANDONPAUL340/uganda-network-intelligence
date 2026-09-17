from time import perf_counter
import pandas as pd
import streamlit as st
from sqlalchemy import text
from src.database import engine
from src.dashboard.logging import get_dashboard_logger

logger = get_dashboard_logger()


def check_database_connection() -> bool:
    """
    Heartbeat Connectivity Checker: Runs a lightweight diagnostic pass 
    to verify database connection pool availability [INDEX].
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1;"))
        return True
    except Exception:
        return False


def read_query(query: str, query_name: str = "dashboard_query", params: dict = None) -> pd.DataFrame:
    """
    Observable Query Execution Engine: Captures precise runtime stopwatch metrics 
    and row counts, logging exceptions automatically if a query fails [INDEX].
    """
    start = perf_counter()
    try:
        with engine.connect() as connection:
            result = pd.read_sql(text(query), connection, params=params)

        duration = perf_counter() - start
        logger.info(
            "Dashboard query completed successfully: name=%s duration=%.4fs rows=%d",
            query_name,
            duration,
            len(result),
        )
        return result

    except Exception as e:
        duration = perf_counter() - start
        logger.exception(
            "Dashboard query execution failed completely: name=%s duration=%.4fs | Error: %s",
            query_name,
            duration,
            str(e),
        )
        raise


# (Keep your check_database_connection and read_query functions exactly as they are)

@st.cache_data(ttl=60)
def get_pipeline_kpis() -> pd.DataFrame:
    """Extracts macro-level pipeline success rates (cached for 60s) [INDEX]."""
    return read_query("SELECT * FROM pipeline_kpis ORDER BY pipeline_name;", "pipeline_kpis")


@st.cache_data(ttl=60)
def get_current_health() -> pd.DataFrame:
    """Extracts the instantaneous real-time health snapshot state (cached for 60s) [INDEX]."""
    return read_query("SELECT * FROM current_pipeline_health ORDER BY checked_at DESC;", "current_pipeline_health")


@st.cache_data(ttl=60)
def get_daily_health() -> pd.DataFrame:
    """Extracts daily historical timeline availability percentage trends (cached for 60s) [INDEX]."""
    return read_query("SELECT * FROM daily_pipeline_health ORDER BY health_date;", "daily_pipeline_health")


@st.cache_data(ttl=60)
def get_stage_summary() -> pd.DataFrame:
    """Extracts micro-stage SLA task execution metrics (cached for 60s) [INDEX]."""
    return read_query("SELECT * FROM pipeline_stage_summary ORDER BY stage_name;", "pipeline_stage_summary")


@st.cache_data(ttl=60)
def get_site_performance(region=None, district=None, start_date=None, end_date=None) -> pd.DataFrame:
    """Extracts cellular tower performance records matching dynamic filters securely [INDEX]."""
    query = """
        SELECT site_id, site_name, region, district, measurement_date, measurement_count,
               avg_traffic_mb, avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct
        FROM gold_site_daily_performance WHERE 1 = 1
    """
    parameters = {}
    if region:
        query += " AND region = :region"
        parameters["region"] = region
    if district:
        query += " AND district = :district"
        parameters["district"] = district
    if start_date:
        query += " AND measurement_date >= :start_date"
        parameters["start_date"] = start_date
    if end_date:
        query += " AND measurement_date <= :end_date"
        parameters["end_date"] = end_date

    query += " ORDER BY measurement_date DESC, site_id;"
    return read_query(query, "site_performance", params=parameters)


@st.cache_data(ttl=60)
def get_network_summary(region=None, district=None, start_date=None, end_date=None) -> pd.DataFrame:
    """Generates high-level network performance metric scores across your towers [INDEX]."""
    query = """
        SELECT COUNT(DISTINCT site_id) AS total_sites, SUM(measurement_count) AS total_measurements,
               ROUND(AVG(avg_traffic_mb), 2) AS avg_traffic_mb, ROUND(AVG(avg_latency_ms), 2) AS avg_latency_ms,
               ROUND(AVG(avg_packet_loss_pct), 2) AS avg_packet_loss_pct, ROUND(AVG(avg_availability_pct), 2) AS avg_availability_pct
        FROM gold_site_daily_performance WHERE 1 = 1
    """
    parameters = {}
    if region:
        query += " AND region = :region"
        parameters["region"] = region
    if district:
        query += " AND district = :district"
        parameters["district"] = district
    if start_date:
        query += " AND measurement_date >= :start_date"
        parameters["start_date"] = start_date
    if end_date:
        query += " AND measurement_date <= :end_date"
        parameters["end_date"] = end_date

    return read_query(query, "network_summary", params=parameters)
def get_database_activity() -> pd.DataFrame:
    """
    Exposes high-resolution query tracking statistics straight out of PostgreSQL 
    internal metadata catalogs to flag locking or long-running database requests [INDEX].
    """
    return read_query(
        """
        SELECT
            pid,
            state,
            query_start,
            now() - query_start AS duration,
            LEFT(query, 150) AS query
        FROM pg_stat_activity
        WHERE datname = current_database()
          AND state <> 'idle'
        ORDER BY query_start;
        """,
        query_name="database_activity",
    )
