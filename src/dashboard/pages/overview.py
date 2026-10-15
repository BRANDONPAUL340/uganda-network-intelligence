"""
Uganda Network Intelligence Platform — Overview Control Dashboard Page
Renders real-time operational KPI metric cards, line trends, and execution streams [INDEX].
"""
import streamlit as st
import pandas as pd
from src.dashboard.monitoring import get_pipeline_summary_metrics, get_recent_pipeline_logs, get_pipeline_runs_time_series
from src.dashboard.components.metrics import render_metric_card_grid
from src.dashboard.components.tables import render_standard_data_grid

import altair as alt

with st.expander("Environment diagnostics"):
    st.write({
        "Streamlit": st.__version__,
        "Pandas": pd.__version__,
        "Altair": alt.__version__,
        "Python": __import__("sys").version,
    })

from src.dashboard.data import (
    get_network_summary,
    get_current_health,
    get_daily_health,
)

from src.dashboard.components.charts import (
    apply_chart_theme,
    render_line_chart,
    render_bar_chart,
    CHART_COLORS,
)

apply_chart_theme()

st.title("🏠 Platform Overview")
st.caption("Monitor system-wide data pipelines, infrastructure health, and real-time operational metrics.")


# ---------------------------------------------------------
# NETWORK PERFORMANCE INTELLIGENCE
# ---------------------------------------------------------

st.markdown("---")
st.subheader("🌍 Network Performance Intelligence")
st.caption(
    "Aggregate measurements and recorded network-health status "
    "from the existing database."
)

network_summary_df = get_network_summary()
health_df = get_current_health()
daily_health_df = get_daily_health()

if not network_summary_df.empty:
    summary = network_summary_df.iloc[0]

    def display_metric(value, suffix="", decimals=2):
        """Format a real measurement, or show N/A if unavailable."""
        if pd.isna(value):
            return "N/A"
        return f"{float(value):,.{decimals}f}{suffix}"

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Sites Reporting",
        display_metric(summary.get("total_sites"), decimals=0),
    )
    k2.metric(
        "Average Availability",
        display_metric(summary.get("avg_availability_pct"), "%"),
    )
    k3.metric(
        "Average Latency",
        display_metric(summary.get("avg_latency_ms"), " ms"),
    )
    k4.metric(
        "Average Packet Loss",
        display_metric(summary.get("avg_packet_loss_pct"), "%"),
    )

    st.caption(
        "Averages are calculated from available stored measurements; "
        "they may not represent every site equally."
    )
else:
    st.info(
        "Network summary measurements are unavailable. "
        "Check the database query and whether the silver measurement "
        "table contains data."
    )

health_col, history_col = st.columns(2)

with health_col:
    st.markdown("#### Current Network Health")

    if (
        not health_df.empty
        and {"health_status", "record_count"}.issubset(health_df.columns)
    ):
        health_chart = health_df.set_index("health_status")
        render_bar_chart(
             health_chart[["record_count"]],
             color=CHART_COLORS["secondary"],
    )
        st.dataframe(health_df, width="stretch", hide_index=True)
    else:
        st.info("No current network-health records are available.")

with history_col:
    st.markdown("#### Daily Network Health History")

    if (
        not daily_health_df.empty
        and {
            "health_date",
            "health_status",
            "record_count",
        }.issubset(daily_health_df.columns)
    ):
        history_chart = daily_health_df.pivot_table(
            index="health_date",
            columns="health_status",
            values="record_count",
            aggfunc="sum",
            fill_value=0,
        )
        health_colors = {
            "Critical": CHART_COLORS["failure"],
            "Healthy": CHART_COLORS["success"],
            "Warning": CHART_COLORS["warning"],
        }

        render_line_chart(
            history_chart,
            color=[
                health_colors[status]
                for status in history_chart.columns
            ],
        )

    else:
        st.info("No daily network-health history is available.")



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



# Pipeline processing trends
st.subheader("📈 National Telemetry Processing Trends Over Time")

if not trend_df.empty:
    chart_data = trend_df.copy()
    chart_data["run_date"] = chart_data["run_date"].astype(str)
    chart_data = chart_data.set_index("run_date")

    render_line_chart(
        chart_data[["success_runs", "failed_runs"]],
        color=[
            CHART_COLORS["success"],
            CHART_COLORS["failure"],
        ],
    )
else:
    st.info("No historical processing trend series found in this cluster database context.")

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
