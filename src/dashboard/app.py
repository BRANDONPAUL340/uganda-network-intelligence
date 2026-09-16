import sys
from pathlib import Path

# ==============================================================================
# 🌌 PROJECT ROADPATH RESOLUTION HOOK
# Resolves ModuleNotFoundError by anchoring the repository root to sys.path [INDEX].
# ==============================================================================
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import plotly.express as px
import streamlit as st

from src.dashboard.data import (
    get_current_health,
    get_daily_health,
    get_pipeline_kpis,
    get_site_performance,
    get_stage_summary,
)


st.set_page_config(
    page_title="Uganda Network Intelligence",
    page_icon="📡",
    layout="wide",
)


st.title("📡 Uganda Network & Service Intelligence")
st.caption("Operational monitoring and network performance dashboard")


# --------------------------------------------------
# Load data
# --------------------------------------------------

try:
    kpis = get_pipeline_kpis()
    current_health = get_current_health()
    daily_health = get_daily_health()
    stage_summary = get_stage_summary()
    site_performance = get_site_performance()

except Exception as exc:
    st.error(f"Unable to load dashboard data: {exc}")
    st.stop()


# --------------------------------------------------
# Current health
# --------------------------------------------------

st.header("Current Pipeline Health")

if current_health.empty:
    st.warning("No pipeline health data is available.")
else:
    health = current_health.iloc[0]

    status = health["overall_status"]

    if status == "HEALTHY":
        st.success(f"Overall Status: {status}")
    elif status == "WARNING":
        st.warning(f"Overall Status: {status}")
    elif status == "CRITICAL":
        st.error(f"Overall Status: {status}")
    else:
        st.info(f"Overall Status: {status}")

    st.caption(
        f"Last checked: {health['checked_at']}"
    )


# --------------------------------------------------
# KPI cards
# --------------------------------------------------

st.header("Operational KPIs")

if kpis.empty:
    st.info("No KPI data is available.")
else:
    kpi = kpis.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Pipeline Success Rate",
        f"{kpi['pipeline_success_rate']:.2f}%"
    )

    col2.metric(
        "Healthy Percentage",
        f"{kpi['healthy_percentage']:.2f}%"
    )

    col3.metric(
        "Total Alerts",
        int(kpi["total_alerts"])
    )

    col4.metric(
        "Critical Alerts",
        int(kpi["total_critical_alerts"])
    )


# --------------------------------------------------
# Health trend
# --------------------------------------------------

st.header("Daily Pipeline Health")

if daily_health.empty:
    st.info("No health trend data is available.")
else:
    chart = px.line(
        daily_health,
        x="health_date",
        y="healthy_percentage",
        markers=True,
        title="Healthy Percentage Over Time",
    )

    chart.update_layout(
        xaxis_title="Date",
        yaxis_title="Healthy Percentage (%)",
    )

    st.plotly_chart(
        chart,
        use_container_width=True,
    )


# --------------------------------------------------
# Stage performance
# --------------------------------------------------

st.header("Pipeline Stage Performance")

if stage_summary.empty:
    st.info("No stage performance data is available.")
else:
    st.dataframe(
        stage_summary,
        use_container_width=True,
    )


# --------------------------------------------------
# Site performance
# --------------------------------------------------

st.header("Network Site Performance")

if site_performance.empty:
    st.info("No site performance data is available.")
else:
    site_names = sorted(
        site_performance["site_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_site = st.selectbox(
        "Select a site",
        ["All sites"] + site_names,
    )

    if selected_site != "All sites":
        filtered = site_performance[
            site_performance["site_name"] == selected_site
        ]
    else:
        filtered = site_performance

    st.dataframe(
        filtered,
        use_container_width=True,
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Uganda Network & Service Intelligence — "
    "PostgreSQL reporting layer + Streamlit dashboard"
)
