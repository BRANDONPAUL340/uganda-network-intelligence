import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from src.database import engine

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def get_parameterized_alert_counts(start_date=None, end_date=None) -> dict:
    """
    15. Operational Summary Metrics: Computes time-slice total, open, 
    and resolved metrics using safe named query parameters [INDEX].
    """
    query = """
        SELECT
            COUNT(*) AS total_alerts,
            COUNT(*) FILTER (WHERE status = 'OPEN') AS open_alerts,
            COUNT(*) FILTER (WHERE status = 'RESOLVED') AS resolved_alerts,
            COUNT(*) FILTER (WHERE DATE(triggered_at) = CURRENT_DATE) AS alerts_today,
            COUNT(*) FILTER (WHERE DATE(resolved_at) = CURRENT_DATE) AS resolved_today
        FROM alert_history
        WHERE 1 = 1
    """
    params = {}
    if start_date:
        query += " AND triggered_at >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND triggered_at <= :end_date"
        params["end_date"] = end_date

    with engine.connect() as conn:
        result = conn.execute(text(query), params).fetchone()
        if not result:
            return {"total_alerts": 0, "open_alerts": 0, "resolved_alerts": 0, "alerts_today": 0, "resolved_today": 0}
        return dict(result._mapping)


def get_parameterized_resolution_summary(start_date=None, end_date=None) -> dict:
    """
    12. Advanced Resolution Time Metrics: Computes average and median 
    durations parameterised by custom date ranges cleanly [INDEX].
    """
    query = """
        SELECT 
            AVG(EXTRACT(EPOCH FROM (resolved_at - triggered_at))) AS average_seconds,
            percentile_cont(0.5) WITHIN GROUP (
                ORDER BY EXTRACT(EPOCH FROM (resolved_at - triggered_at))
            ) AS median_seconds
        FROM alert_history
        WHERE status = 'RESOLVED' AND resolved_at IS NOT NULL
    """
    params = {}
    if start_date:
        query += " AND triggered_at >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND triggered_at <= :end_date"
        params["end_date"] = end_date

    with engine.connect() as conn:
        result = conn.execute(text(query), params).fetchone()
        if not result or result._mapping["average_seconds"] is None:
            return {"average_seconds": 0.0, "median_seconds": 0.0}
        return {
            "average_seconds": round(float(result._mapping["average_seconds"] or 0) / 60, 1), # Return in minutes
            "median_seconds": round(float(result._mapping["median_seconds"] or 0) / 60, 1)   # Return in minutes
        }


def get_parameterized_daily_trends(start_date=None, end_date=None) -> pd.DataFrame:
    """
    10. Created vs Resolved Volume Trend: Compares daily execution 
    patterns across custom timeline intervals [INDEX].
    """
    query = """
        SELECT 
            COALESCE(c.alert_date, r.resolved_date) AS tracking_date,
            COALESCE(c.created_count, 0) AS created_count,
            COALESCE(r.resolved_count, 0) AS resolved_count
        FROM (
            SELECT DATE(triggered_at) AS alert_date, COUNT(*) AS created_count
            FROM alert_history GROUP BY DATE(triggered_at)
        ) c
        FULL OUTER JOIN (
            SELECT DATE(resolved_at) AS resolved_date, COUNT(*) AS resolved_count
            FROM alert_history WHERE resolved_at IS NOT NULL GROUP BY DATE(resolved_at)
        ) r ON c.alert_date = r.resolved_date
        WHERE 1 = 1
    """
    params = {}
    if start_date:
        query += " AND (c.alert_date >= :start_date OR r.resolved_date >= :start_date)"
        params["start_date"] = start_date
    if end_date:
        query += " AND (c.alert_date <= :end_date OR r.resolved_date <= :end_date)"
        params["end_date"] = end_date
    query += " ORDER BY tracking_date;"

    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)


def get_parameterized_alert_recurrence(start_date=None, end_date=None) -> pd.DataFrame:
    """
    11. Recurrence Frequency Analysis: Isolates repetitive operational 
    vulnerabilities using secure named SQL parameter filters [INDEX].
    """
    query = """
        SELECT alert_name, COUNT(*) AS occurrences
        FROM alert_history
        WHERE 1 = 1
    """
    params = {}
    if start_date:
        query += " AND triggered_at >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND triggered_at <= :end_date"
        params["end_date"] = end_date
    query += " GROUP BY alert_name ORDER BY occurrences DESC;"

    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)
