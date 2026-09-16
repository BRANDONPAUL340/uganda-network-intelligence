
import sys
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Project root path resolution
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import plotly.express as px
import streamlit as st

# --------------------------------------------------
# Centralized configuration
# --------------------------------------------------

from src.config import PIPELINE_NAME

# --------------------------------------------------
# Dashboard data access
# --------------------------------------------------

from src.dashboard.data import (
    check_database_connection,
    get_current_health,
    get_daily_health,
    get_pipeline_kpis,
    get_site_performance,
    get_stage_summary,
)


# --------------------------------------------------
# Streamlit configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Uganda Network & Service Intelligence",
    page_icon="📡",
    layout="wide",
)

st.title("📡 Uganda Network & Service Intelligence")
st.caption(f"Operational monitoring dashboard — pipeline: {PIPELINE_NAME}")

# --------------------------------------------------
# Operational Cache Management Control
# --------------------------------------------------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()  # Evicts all cached entries out of memory
    st.rerun()             # Re-triggers the execution thread

st.markdown("---")
# ... (the rest of the data loading safety gates and presentation blocks follow)



# --------------------------------------------------
# Database Connectivity Safety Gate
# --------------------------------------------------

if not check_database_connection():
    st.error(
        "🚨 **Database connection unavailable.** "
        "Please check your PostgreSQL instance state and your "
        "`DATABASE_URL` environment configuration."
    )
    st.stop()


# --------------------------------------------------
# Load dashboard data
# --------------------------------------------------

try:
    kpis = get_pipeline_kpis()
    current_health = get_current_health()
    daily_health = get_daily_health()
    stage_summary = get_stage_summary()
    site_performance = get_site_performance()

except Exception as exc:
    st.error(
        f"🚨 **Unable to load dashboard data:** {exc}"
    )
    st.stop()


# --------------------------------------------------
# Current Pipeline Health
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
# Operational KPIs
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
# Daily Pipeline Health
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
# Pipeline Stage Performance
# --------------------------------------------------

st.header("Pipeline Stage Performance")

if stage_summary.empty:
    st.info("No stage performance data is available.")

else:
    st.dataframe(
        stage_summary,
        use_container_width=True,
    )


# (Keep all of the top sidebar filter logic, date pickers, and health checks intact)

# --------------------------------------------------
# Network Performance Executive Summary KPI Cards
# --------------------------------------------------
st.header("📊 Network Performance Summary")

if network_summary.empty or network_summary.iloc[0]["total_sites"] is None:
    st.warning("No network performance data matches the selected filter criteria.")
else:
    summary = network_summary.iloc[0]

    # Create a 5-column dashboard configuration for high-level summary cards [INDEX]
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Monitored Sites",
        int(summary["total_sites"] or 0)
    )
    col2.metric(
        "Total Measurements",
        f"{int(summary['total_measurements'] or 0):,}"
    )
    col3.metric(
        "Avg Traffic (MB)",
        f"{float(summary['avg_traffic_mb'] or 0.0):.2f}"
    )
    col4.metric(
        "Avg Latency (ms)",
        f"{float(summary['avg_latency_ms'] or 0.0):.2f}"
    )
    col5.metric(
        "Core Availability",
        f"{float(summary['avg_availability_pct'] or 0.0):.2f}%"
    )

    # 11. Core Network Quality Metric Card
    st.metric(
        "Average Network Packet Loss",
        f"{float(summary['avg_packet_loss_pct'] or 0.0):.2f}%",
        delta=None
    )


# --------------------------------------------------
# Network Site Performance Data Table
# --------------------------------------------------
st.header("📡 Detailed Site Performance Logs")

if site_performance.empty:
    st.info("No parameterized site performance data matches your filter criteria.")
else:
    # Display the filtered rows directly out of database calculations [INDEX]
    st.dataframe(
        site_performance[[
            "site_name", "region", "district", "measurement_date", "measurement_count",
            "avg_traffic_mb", "avg_latency_ms", "avg_packet_loss_pct", "avg_availability_pct"
        ]], 
        use_container_width=True, 
        hide_index=True
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption(
    "Uganda Network & Service Intelligence — "
    "PostgreSQL reporting layer + Streamlit dashboard"
)
