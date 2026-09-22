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
