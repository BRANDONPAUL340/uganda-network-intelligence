import pandas as pd
from sqlalchemy import text
from src.database import engine


def read_query(query: str) -> pd.DataFrame:
    """
    Safely handles connection pooling to execute SQL statements 
    and returns a structured Pandas DataFrame directly from the database [INDEX].
    """
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)


def get_pipeline_kpis() -> pd.DataFrame:
    """Extracts macro-level pipeline success rates and availability metrics [INDEX]."""
    return read_query(
        """
        SELECT *
        FROM pipeline_kpis
        ORDER BY pipeline_name;
        """
    )


def get_current_health() -> pd.DataFrame:
    """Extracts the instantaneous global real-time health snapshot state [INDEX]."""
    return read_query(
        """
        SELECT *
        FROM current_pipeline_health
        ORDER BY checked_at DESC;
        """
    )


def get_daily_health() -> pd.DataFrame:
    """Extracts daily historical timeline availability percentage trends [INDEX]."""
    return read_query(
        """
        SELECT *
        FROM daily_pipeline_health
        ORDER BY health_date;
        """
    )


def get_stage_summary() -> pd.DataFrame:
    """Extracts micro-stage SLA task execution metrics and processing counts [INDEX]."""
    return read_query(
        """
        SELECT *
        FROM pipeline_stage_summary
        ORDER BY stage_name;
        """
    )


def get_site_performance() -> pd.DataFrame:
    """
    Extracts deep analytical cellular tower performance summaries 
    natively computed inside our Gold aggregations table tier [INDEX].
    """
    return read_query(
        """
        SELECT
            site_id,
            site_name,
            region,
            district,
            measurement_date,
            measurement_count,
            avg_traffic_mb,
            avg_latency_ms,
            avg_packet_loss_pct,
            avg_signal_strength_dbm,
            avg_availability_pct
        FROM gold_site_daily_performance
        ORDER BY measurement_date DESC, site_id;
        """
    )
