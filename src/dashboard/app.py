import sys
from datetime import date, datetime, timezone
from pathlib import Path
import pandas as pd

# ==============================================================================
# 🌌 PROJECT PATHWAY RESOLUTION HOOK
# Resolves ModuleNotFoundError by anchoring the repository root to sys.path [INDEX].
# ==============================================================================
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import plotly.express as px
import streamlit as st

from src.config import PIPELINE_NAME
from src.dashboard.health import check_dashboard_database
from src.dashboard.version import DASHBOARD_VERSION
from src.dashboard.monitoring import get_open_alerts, get_recent_alerts
from src.monitoring.alert_metrics import (
    get_parameterized_alert_counts,
    get_parameterized_resolution_summary,
    get_parameterized_daily_trends,
    get_parameterized_alert_recurrence,
)
from src.dashboard.data import (
    check_database_connection,
    get_current_health,
    get_daily_health,
    get_database_activity,
    get_network_summary,
    get_pipeline_kpis,
    get_site_performance,
    get_stage_summary,
)

st.set_page_config(
    page_title="Uganda Network & Service Intelligence",
    page_icon="📡",
    layout="wide",
)

st.title("📡 Uganda Network & Service Intelligence Console")
st.caption(f"Operational Cockpit & Incident Analytics — Pipeline: {PIPELINE_NAME}")

if st.button("🔄 Refresh Application Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# ==============================================================================
# 🎛️ SIDEBAR INTERACTIVE CONTROL FILTERS & LIVE HEALTH INDICATOR
# ==============================================================================
st.sidebar.header("Dashboard Filters")
dashboard_health = check_dashboard_database()

if dashboard_health["status"] == "HEALTHY":
    st.sidebar.success("Database: Healthy")
else:
    st.sidebar.error("Database: Critical")

st.sidebar.caption(f"Dashboard version: {DASHBOARD_VERSION}")

try:
    all_sites_base = get_site_performance()
except Exception as exc:
    st.error(f"Unable to initialize filter datasets: {exc}")
    st.stop()

# 🌍 A. Geographic & Timeline Filters
regions = sorted(all_sites_base["region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region", ["All regions"] + regions)
region_filter = None if selected_region == "All regions" else selected_region

all_sites_base["measurement_date"] = pd.to_datetime(all_sites_base["measurement_date"]).dt.date
min_date = all_sites_base["measurement_date"].min() if not all_sites_base.empty else date.today()
max_date = all_sites_base["measurement_date"].max() if not all_sites_base.empty else date.today()

selected_dates = st.sidebar.date_input(
    "Operational analytical range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date, end_date = min_date, max_date

# FETCH METRIC DATA PANELS
try:
    kpis = get_pipeline_kpis()
    current_health = get_current_health()
    daily_health = get_daily_health()
    stage_summary = get_stage_summary()
    open_alerts = get_open_alerts()
    recent_alerts = get_recent_alerts()
    
    # Ingest dynamic parameterised analytics [INDEX]
    metrics_counts = get_parameterized_alert_counts(start_date, end_date)
    res_summary = get_parameterized_resolution_summary(start_date, end_date)
    trend_df = get_parameterized_daily_trends(start_date, end_date)
    recurrence_df = get_parameterized_alert_recurrence(start_date, end_date)
    
    network_summary = get_network_summary(region=region_filter, start_date=start_date, end_date=end_date)
    site_performance = get_site_performance(region=region_filter, start_date=start_date, end_date=end_date)
except Exception as exc:
    st.error(f"Unable to synchronize analytics data frames: {exc}")
    st.stop()


# ==============================================================================
# 🟢 CONTAINER SECTION 1: Pipeline Health Summary
# ==============================================================================
st.header("🟢 Core Pipeline Infrastructure Health")
if current_health.empty:
    st.warning("No pipeline health indicators available.")
else:
    pipeline_status = current_health.iloc["overall_status"]
    if pipeline_status == "HEALTHY":
        st.success(f"Pipeline Health Status: **{pipeline_status}** (⚡ Engine operating normally)")
    else:
        st.error(f"Pipeline Health Status: **{pipeline_status}** (⚠️ Active system delay tracked)")


# ==============================================================================
# 📊 CONTAINER SECTION 2: Labeled Operational Summary (Step 15)
# ==============================================================================
st.markdown("---")
st.header("📋 Incident Operational Summary")

col_op1, col_op2, col_op3, col_op4, col_op5 = st.columns(5)
col_op1.metric("Active Open Alerts", int(metrics_counts["open_alerts"]))
col_op2.metric("Alerts Triggered Today", int(metrics_counts["alerts_today"]))
col_op3.metric("Alerts Resolved Today", int(metrics_counts["resolved_today"]))
col_op4.metric("Avg Resolution Time", f"{res_summary['average_seconds']}m")
col_op5.metric("Median Resolution Time", f"{res_summary['median_seconds']}m")


# ==============================================================================
# 📉 CONTAINER SECTION 3: Alert Analytics & Trends (Step 12 & 13)
# ==============================================================================
st.markdown("---")
st.header("📉 Multi-Dimensional Alert Analytics")

col_an1, col_an2 = st.columns(2)

with col_an1:
    st.subheader("🗓️ Incident Volume Time-Series Trend")
    if trend_df.empty:
        st.info("No time-series data matches your chosen date window.")
    else:
        # Melt dataframe to plot created vs resolved comparisons natively
        melted_df = trend_df.melt(id_vars=["tracking_date"], value_vars=["created_count", "resolved_count"],
                                  var_name="Metric Type", value_name="Incident Count")
        fig_trend = px.line(melted_df, x="tracking_date", y="Incident Count", color="Metric Type",
                            markers=True, title="Alerts Created vs Alerts Resolved Over Time")
        st.plotly_chart(fig_trend, use_container_width=True)

with col_an2:
    st.subheader("🔄 Recurring Incident Distribution Check")
    if recurrence_df.empty:
        st.info("No recurring anomalies found inside this range window.")
    else:
        fig_rec = px.bar(recurrence_df, x="occurrences", y="alert_name", orientation="h",
                         title="Alert Volume Recurrence Density by Type",
                         labels={"occurrences": "Total Occurrence Frequency", "alert_name": "Alert Name Type"})
        st.plotly_chart(fig_rec, use_container_width=True)


# ==============================================================================
# 📡 CONTAINER SECTION 4: Network Metrics & Drill Downs
# ==============================================================================
st.markdown("---")
st.header("📊 Cellular Sites Performance Metrics")
if network_summary.empty or network_summary.iloc["total_sites"] is None:
    st.warning("No cellular tower performance values found within these filter targets.")
else:
    summary = network_summary.iloc
    col_net1, col_net2, col_net3, col_net4 = st.columns(4)
    col_net1.metric("Active Towers", int(summary["total_sites"] or 0))
    col_net2.metric("Total Ingested Data (MB)", f"{float(summary['avg_traffic_mb'] or 0):,.2f}")
    col_net3.metric("Avg Latency Metric", f"{float(summary['avg_latency_ms'] or 0):.2f}ms")
    col_net4.metric("Tower Link Availability", f"{float(summary['avg_availability_pct'] or 0):.2f}%")


# ==============================================================================
# 🔧 CONTAINER SECTION 5: Platform Engine Diagnostics Expander Logs
# ==============================================================================
st.markdown("---")
st.header("🔧 Platform Engine Diagnostics")
with st.expander("Active Database Activity Stream (pg_stat_activity)"):
    try:
        activity = get_database_activity()
        if activity.empty:
            st.info("No queries currently executing outside idle connection pools.")
        else:
            st.dataframe(activity, use_container_width=True, hide_index=True)
    except Exception as exc:
        st.warning(f"Could not extract process tracking parameters: {exc}")

st.divider()
st.caption("Uganda Network & Service Intelligence Data Platform — PostgreSQL 18 analytics view")
