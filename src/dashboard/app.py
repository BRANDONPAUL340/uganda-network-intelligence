
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from src.dashboard.monitoring import get_pipeline_summary_metrics

# ---------------------------------------------------------------------------
# Global Page Configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Uganda Network Intelligence Platform",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Sidebar Branding
# ---------------------------------------------------------------------------

st.sidebar.title("🌍 UGANDA NETWORK")
st.sidebar.subheader("INTELLIGENCE")
st.sidebar.markdown("---")


# ---------------------------------------------------------------------------
# Database Health Check
# ---------------------------------------------------------------------------

try:
    health = get_pipeline_summary_metrics()
    db_connected = health.get("status") == "HEALTHY"

except Exception:
    db_connected = False


# ---------------------------------------------------------------------------
# Multi-Page Navigation
# ---------------------------------------------------------------------------
#
# The Input Data page is the final operational ingestion interface.
#
# Event Store Worker Monitoring remains intentionally excluded because its
# underlying persistence model is not part of the authoritative schema.
#
# Lineage remains active because pipeline_lineage is present and verified.
# ---------------------------------------------------------------------------

pages = {
    "📊 Dashboard Operational Views": [
        st.Page(
            "pages/overview.py",
            title="Platform Overview",
            icon="🏠",
            default=True,
        ),
        st.Page(
            "pages/pipeline_runs.py",
            title="Pipeline Execution Logs",
            icon="🔄",
        ),
    ],

    "📡 Telemetry & Metrics": [
        st.Page(
            "pages/data_quality.py",
            title="Data Quality Engine",
            icon="✅",
        ),
        st.Page(
            "pages/incidents.py",
            title="Incident Management Panel",
            icon="🚨",
        ),
    ],

    "🧭 Data Lineage": [
        st.Page(
            "pages/lineage.py",
            title="Data Lineage Map",
            icon="🧭",
        ),
    ],

    "📝 Data Operations": [
        st.Page(
            "pages/input_data.py",
            title="Input Data",
            icon="📝",
        ),
    ],
}


# ---------------------------------------------------------------------------
# Navigation Router
# ---------------------------------------------------------------------------

navigation_router = st.navigation(pages)


# ---------------------------------------------------------------------------
# Sidebar Infrastructure Status
# ---------------------------------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.markdown("### 🖥️ System Infrastructure")

if db_connected:
    st.sidebar.success("🟢 PostgreSQL 18: Connected")
else:
    st.sidebar.error("🔴 PostgreSQL 18: Disconnected")

st.sidebar.caption("Workstation Node Location: Kampala, Uganda")


# ---------------------------------------------------------------------------
# Execute Selected Page
# ---------------------------------------------------------------------------

navigation_router.run()