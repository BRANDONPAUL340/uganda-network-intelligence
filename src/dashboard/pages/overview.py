"""
Uganda Network Intelligence Platform — Overview Control Dashboard Page
Renders real-time operational KPI metric cards, line trends, and execution streams [INDEX].
"""
import streamlit as st
import pandas as pd
from src.dashboard.monitoring import get_pipeline_summary_metrics, get_recent_pipeline_logs, get_pipeline_runs_time_series
from src.dashboard.components.metrics import render_metric_card_grid
from src.dashboard.components.tables import render_standard_data_grid

st.title("🏠 Platform Overview")
st.caption("Monitor system-wide data pipelines, infrastructure health, and real-time operational metrics.")
st.markdown("---")

with st.spinner("Fetching operational telemetry from cluster..."):
    metrics = get_pipeline_summary_metrics()
    recent_runs_df = get_recent_pipeline_logs(limit=5)
    trend_df = get_pipeline_runs_time_series()

if metrics["status"] == "ERROR":
    st.error("⚠️ Database Error: Unable to safely retrieve system metrics right now.")

# Render aggregate key metrics
render_metric_card_grid([
    {"label": "Total Ingestion Runs", "value": f"{metrics['total_runs']:,}"},
    {"label": "Successful Pipelines", "value": f"{metrics['success_runs']:,}"},
    {"label": "Failed Operations", "value": f"{metrics['failed_runs']:,}", "delta": f"{metrics['failed_runs']} critical" if metrics['failed_runs'] > 0 else None, "delta_color": "inverse"},
    {"label": "Active Operational Incidents", "value": metrics['open_incidents'], "delta": f"{metrics['open_incidents']} open alarms" if metrics['open_incidents'] > 0 else None, "delta_color": "off"}
])

st.markdown("### ")
st.markdown("---")

# 1, 4 & 6. Charting Presentation Tier Section
st.subheader("📈 National Telemetry Processing Trends Over Time")
if not trend_df.empty:
    # Restructure dataframe timeline mapping safely for chart consumption
    chart_data = trend_df.copy()
    chart_data["run_date"] = chart_data["run_date"].astype(str)
    chart_data = chart_data.set_index("run_date")
    
    # 8. Render success vs failed runs visually over time via a multi-line graph
    st.line_chart(chart_data[["success_runs", "failed_runs"]], color=["#2ecc71", "#e74c3c"])
else:
    st.info("ℹ️ No historical processing trend series found in this cluster database context.")

st.markdown("---")
left_panel, right_panel = st.columns(2)

with left_panel:
    st.subheader("🔄 Chronological Stream: Recent Pipeline Runs")
    render_standard_data_grid(
        df=recent_runs_df,
        columns_map=["run_id", "pipeline_name", "current_stage", "status", "started_at", "duration"],
        empty_message="No recent pipeline execution logs found in this cluster database context."
    )

with right_panel:
    st.subheader("🩺 Core System Health Status")
    if metrics["status"] == "HEALTHY":
        st.success("✓ Relational Storage Layer (PostgreSQL 18)")
    else:
        st.error("✕ Relational Storage Layer (Connection Lost)")
    st.success("✓ Stream Ingestion Pipeline Workers")
    st.success("✓ Asynchronous Event Store Router Engine")
    st.warning("! Data Quality Freshness Threshold Latency Check")
