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
from src.dashboard.monitoring import (
    get_open_alerts,
    get_recent_alerts,
    get_alert_summary_by_severity,
    get_alert_summary_by_status,
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

# Page Layout Configurations
st.set_page_config(
    page_title="Uganda Network & Service Intelligence",
    page_icon="📡",
    layout="wide",
)

dashboard_checked_at = datetime.now(timezone.utc)

st.title("📡 Uganda Network & Service Intelligence")
st.caption(f"Operational Monitoring Dashboard — Pipeline: {PIPELINE_NAME}")
st.caption(f"Dashboard snapshot timestamp: {dashboard_checked_at:%Y-%m-%d %H:%M:%S} UTC")

# Operational Cache Management Control
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# Database Connectivity Safety Gate Check
if not check_database_connection():
    st.error(
        "🚨 **Database connection unavailable.** "
        "Please check your PostgreSQL instance state and your DATABASE_URL environment configuration parameters."
    )
    st.stop()


# ==============================================================================
# 🎛️ SIDEBAR INTERACTIVE CONTROL FILTERS & LIVE HEALTH INDICATOR
# ==============================================================================
st.sidebar.header("Dashboard Filters")

dashboard_health = check_dashboard_database()

if dashboard_health["status"] == "HEALTHY":
    st.sidebar.success("Database: Healthy")
elif dashboard_health["status"] == "WARNING":
    st.sidebar.warning("Database: Warning")
else:
    st.sidebar.error("Database: Critical")

st.sidebar.caption(f"Dashboard version: {DASHBOARD_VERSION}")

try:
    all_sites_base = get_site_performance()
except Exception as exc:
    st.error(f"Unable to initialize filter datasets: {exc}")
    st.stop()

# 🌍 A. Dynamic Region Selection Filter
regions = sorted(all_sites_base["region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region", ["All regions"] + regions)

region_filter = None if selected_region == "All regions" else selected_region

# 🏢 B. Cascading District Selection Filter
district_source = all_sites_base
if region_filter:
    district_source = district_source[district_source["region"] == region_filter]

districts = sorted(district_source["district"].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("District", ["All districts"] + districts)

district_filter = None if selected_district == "All districts" else selected_district

# 📅 C. Chronological Timeline Date Picker Bounds Filter
if not all_sites_base.empty:
    all_sites_base["measurement_date"] = pd.to_datetime(all_sites_base["measurement_date"]).dt.date
    min_date = all_sites_base["measurement_date"].min()
    max_date = all_sites_base["measurement_date"].max()
else:
    min_date = date.today()
    max_date = date.today()

selected_dates = st.sidebar.date_input(
    "Measurement date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = min_date
    end_date = max_date


# FETCH PARAMETERIZED METRIC DATA PANELS
try:
    kpis = get_pipeline_kpis()
    current_health = get_current_health()
    daily_health = get_daily_health()
    stage_summary = get_stage_summary()
    
    # Ingest incident monitoring modules data [INDEX]
    open_alerts = get_open_alerts()
    recent_alerts = get_recent_alerts()
    severity_summary = get_alert_summary_by_severity()
    
    network_summary = get_network_summary(
        region=region_filter,
        district=district_filter,
        start_date=start_date,
        end_date=end_date
    )
    site_performance = get_site_performance(
        region=region_filter,
        district=district_filter,
        start_date=start_date,
        end_date=end_date
    )
except Exception as exc:
    st.error(f"Unable to synchronize parameterized data views: {exc}")
    st.stop()


# ==============================================================================
# 🚨 OPERATIONS & MONITORING SECTION (Day 115 Core Architecture Feature Block)
# =============================================================================
st.header("🚨 Operations & Monitoring Center")

# 6. Add dynamic monitoring KPIs pulled natively out of PostgreSQL logs [INDEX]
total_open_count = len(open_alerts) if not open_alerts.empty else 0

sev2_count = 0
sev3_count = 0
if not severity_summary.empty:
    sev_mapping = dict(zip(severity_summary["severity"], severity_summary["alert_count"]))
    sev2_count = sev_mapping.get("SEV2", 0)
    sev3_count = sev_mapping.get("SEV3", 0)

pipeline_latest_status = "UNKNOWN"
if not current_health.empty:
    pipeline_latest_status = current_health.iloc[0]["overall_status"]

col_alert1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
with col_alert1:
    if total_open_count > 0:
        st.metric("🚨 Active Open Alerts", total_open_count, delta="- Actions Required", delta_color="inverse")
    else:
        st.metric("🚨 Active Open Alerts", total_open_count)
with col_kpi2:
    st.metric("🟡 Active SEV2 Alerts", int(sev2_count))
with col_kpi3:
    st.metric("🔵 Active SEV3 Alerts", int(sev3_count))
with col_kpi4:
    if pipeline_latest_status == "HEALTHY":
        st.metric("📡 Pipeline Status", pipeline_latest_status, delta="⚡ Normal")
    else:
        st.metric("📡 Pipeline Status", pipeline_latest_status, delta="⚠️ Anomaly Detected", delta_color="inverse")

# 7. Layout Breakdown Containers
st.markdown("---")
col_mon_left, col_mon_right = st.columns([3, 2])

with col_mon_left:
    # 8. Display Open Active Incidents Table Grid with high visibility
    st.subheader("⚠️ Active Open Incidents")
    if open_alerts.empty:
        st.success("🎉 **System Clean:** Absolute zero unresolved platform anomalies found on disk.")
    else:
        # 10. Perform high-resolution python presentation age calculations [INDEX]
        # Ensure triggered_at series handles timezone conversion safely to prevent math bugs
        open_alerts["triggered_at"] = pd.to_datetime(open_alerts["triggered_at"])
        now_ts = datetime.now(timezone.utc)
        
        ages_formatted = []
        for idx, row in open_alerts.iterrows():
            trig_time = row["triggered_at"]
            if trig_time.tzinfo is None:
                trig_time = trig_time.replace(tzinfo=timezone.utc)
            else:
                trig_time = trig_time.tz_convert(timezone.utc)
                
            delta = now_ts - trig_time
            tot_min = int(delta.total_seconds() // 60)
            if tot_min >= 60:
                hours = tot_min // 60
                mins = tot_min % 60
                ages_formatted.append(f"{hours}h {mins}m")
            else:
                ages_formatted.append(f"{tot_min}m")
                
        open_alerts["Open for"] = ages_formatted
        
        # Display polished incident panel to engineers [INDEX]
        st.dataframe(
            open_alerts[["severity", "alert_name", "message", "Open for", "triggered_at"]],
            use_container_width=True,
            hide_index=True
        )

with col_mon_right:
    # 9. Recent Alert History Log Table (Audit trail mapping) [INDEX]
    st.subheader("📚 Recent Alert History Logs")
    if recent_alerts.empty:
        st.info("No historical alerts registered inside audit table ledgers.")
    else:
        st.dataframe(
            recent_alerts[["alert_name", "severity", "status", "triggered_at"]],
            use_container_width=True,
            hide_index=True
        )

# Pipeline Platform Ingestion Health Trend Sub-container
st.subheader("📈 Pipeline Availability Statistics")
col_trend_left, col_trend_right = st.columns(2)

with col_trend_left:
    if daily_health.empty:
        st.info("No health trend timeline data is available.")
    else:
        chart = px.line(
            daily_health,
            x="health_date",
            y="healthy_percentage",
            markers=True,
            title="Platform Availability Over Time (%)",
        )
        chart.update_layout(xaxis_title="Date", yaxis_title="Healthy Percentage (%)")
        st.plotly_chart(chart, use_container_width=True)

with col_trend_right:
    if daily_health.empty:
        st.info("No health trend distribution data available.")
    else:
        health_counts = (
            daily_health[["healthy_checks", "warning_checks", "critical_checks"]]
            .sum()
            .reset_index()
        )
        health_counts.columns = ["status", "count"]
        health_counts["status"] = (
            health_counts["status"]
            .str.replace("_checks", "", regex=False)
            .str.upper()
        )

        fig_pie = px.pie(
            health_counts,
            names="status",
            values="count",
            title="Pipeline Health State Distribution Share",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# 12. Add a performance-safe 30-second interface auto-refresh loop fence [1]
import time
st.sidebar.markdown("---")
if st.sidebar.checkbox("🔄 Enable Auto-Refresh (30s)", value=True):
    time.sleep(0.5)  # Safe GUI thread breathing room
    st.fragment(st.rerun)()  # Triggers a safe layout reload loop fence

