import sys
from datetime import date
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
from src.dashboard.data import (
    check_database_connection,
    get_current_health,
    get_daily_health,
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

st.title("📡 Uganda Network & Service Intelligence")
st.caption(f"Operational Monitoring & Network Performance KPI Center — Pipeline: {PIPELINE_NAME}")

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
# 🎛️ SIDEBAR INTERACTIVE CONTROL FILTERS
# ==============================================================================
st.sidebar.header("Dashboard Filters")

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
# 🟢 CONTAINER SECTION 1: Current Pipeline Health Banner
# ==============================================================================
st.header("🟢 Current Pipeline Health")

if current_health.empty:
    st.warning("No pipeline health data is available.")
else:
    health = current_health.iloc[0]
    status = health["overall_status"]

    if status == "HEALTHY":
        st.success(f"Overall Status: **{status}**")
    elif status == "WARNING":
        st.warning(f"Overall Status: **{status}**")
    elif status == "CRITICAL":
        st.error(f"Overall Status: **{status}**")
    else:
        st.info(f"Overall Status: **{status}**")

    st.caption(f"Last checked: {health['checked_at']}")


# ==============================================================================
# 📊 CONTAINER SECTION 2: Macro Platform Performance KPIs
# ==============================================================================
st.markdown("---")
st.header("📊 Executive Performance KPIs")

if kpis.empty:
    st.info("No KPI data is available.")
else:
    kpi = kpis.iloc[0]
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Pipeline Success Rate", f"{kpi['pipeline_success_rate']:.2f}%")
    col2.metric("Healthy Percentage", f"{kpi['healthy_percentage']:.2f}%")
    col3.metric("Total System Alerts", int(kpi["total_alerts"]))
    col4.metric("Critical System Alerts", int(kpi["total_critical_alerts"]))


# ==============================================================================
# 📊 CONTAINER SECTION 3: Network Performance Summary Row
# ==============================================================================
st.markdown("---")
st.header("📡 Network Performance Summary")

if network_summary.empty or network_summary.iloc[0]["total_sites"] is None:
    st.warning("No network performance data matches the selected filter criteria.")
else:
    summary = network_summary.iloc[0]
    col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)

    col_kpi1.metric("Active Sites", int(summary["total_sites"] or 0))
    col_kpi2.metric("Total Measurements", f"{int(summary['total_measurements'] or 0):,}")
    col_kpi3.metric("Avg Traffic (MB)", f"{float(summary['avg_traffic_mb'] or 0.0):.2f}")
    col_kpi4.metric("Avg Latency (ms)", f"{float(summary['avg_latency_ms'] or 0.0):.2f}")
    col_kpi5.metric("Core Availability", f"{float(summary['avg_availability_pct'] or 0.0):.2f}%")

    st.metric(
        "Average Network Packet Loss",
        f"{float(summary['avg_packet_loss_pct'] or 0.0):.2f}%",
        delta=None
    )


# ==============================================================================
# 📈 CONTAINER SECTION 4: Network Trends Visual Analytics
# ==============================================================================
st.markdown("---")
if not site_performance.empty:
    st.header("📈 Network Performance & Trend Analytics")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        site_chart_data = (
            site_performance
            .groupby("site_name", as_index=False)["avg_availability_pct"]
            .mean()
            .sort_values("avg_availability_pct")
        )
        fig_avail = px.bar(
            site_chart_data,
            x="avg_availability_pct",
            y="site_name",
            orientation="h",
            title="Average Site Availability (%)",
            labels={"avg_availability_pct": "Availability (%)", "site_name": "Site Name"},
        )
        st.plotly_chart(fig_avail, use_container_width=True)

    with col_chart2:
        latency_data = (
            site_performance
            .groupby("site_name", as_index=False)["avg_latency_ms"]
            .mean()
            .sort_values("avg_latency_ms", ascending=False)
        )
        fig_lat = px.bar(
            latency_data,
            x="site_name",
            y="avg_latency_ms",
            title="Average Latency by Site (ms)",
            labels={"avg_latency_ms": "Latency (ms)", "site_name": "Site Name"},
        )
        st.plotly_chart(fig_lat, use_container_width=True)

    traffic_trend = (
        site_performance
        .groupby("measurement_date", as_index=False)["avg_traffic_mb"]
        .mean()
    )
    fig_traffic = px.line(
        traffic_trend,
        x="measurement_date",
        y="avg_traffic_mb",
        markers=True,
        title="Average Network Traffic Over Time (MB)",
        labels={"measurement_date": "Timeline Date", "avg_traffic_mb": "Traffic Volume (MB)"},
    )
    st.plotly_chart(fig_traffic, use_container_width=True)


# ==============================================================================
# 🩺 CONTAINER SECTION 5: Pipeline Health Timeline & Distribution
# ==============================================================================
st.markdown("---")
st.header("🩺 Pipeline Health History Profiles")
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
        )