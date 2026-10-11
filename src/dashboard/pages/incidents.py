import streamlit as st
from src.dashboard.monitoring import (
    get_incidents_summary_metrics,
    get_filtered_incidents_logs,
    get_incidents_severity_distribution,
)
from src.dashboard.components.metrics import render_metric_card_grid
from src.dashboard.components.tables import render_standard_data_grid
# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------
st.title("🚨 Incidents")
st.caption(
    "Investigate operational incidents, evaluate severity levels, "
    "and perform infrastructure triage."
)
st.markdown("---")
# ---------------------------------------------------------------------------
# Incident Metrics
# ---------------------------------------------------------------------------
with st.spinner("Analyzing operational incident states..."):
    metrics = get_incidents_summary_metrics()
    severity_df = get_incidents_severity_distribution()
# ---------------------------------------------------------------------------
# Database / Extraction Error Handling
# ---------------------------------------------------------------------------
if "error" in metrics:
    st.error(
        "⚠️ Database Error: Unable to safely query current incident logs."
    )

    st.caption(str(metrics["error"]))
# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
render_metric_card_grid(
    [
        {
            "label": "Total Logged Issues",
            "value": f"{metrics['total_incidents']:,}",
        },
        {
            "label": "🔓 Unresolved Alarms",
            "value": f"{metrics['open_incidents']:,}",
            "delta": (
                f"{metrics['open_incidents']} active"
                if metrics["open_incidents"] > 0
                else None
            ),
            "delta_color": "inverse",
        },
        {
            "label": "⚠️ Critical / High Priority",
            "value": f"{metrics['critical_high_incidents']:,}",
            "delta": (
                f"{metrics['critical_high_incidents']} recorded"
                if metrics["critical_high_incidents"] > 0
                else None
            ),
            "delta_color": "off",
        },
        {
            "label": "✅ Resolved Tickets",
            "value": f"{metrics['resolved_incidents']:,}",
        },
    ]
)


# ---------------------------------------------------------------------------
# Severity Distribution
# ---------------------------------------------------------------------------

st.markdown("### ")
st.subheader("📊 Incident Distribution by Severity Classification")

if not severity_df.empty:

    chart_data = severity_df.copy().set_index("severity")

    st.bar_chart(
        chart_data["incident_count"],
    )

else:
    st.info(
        "ℹ️ No incident severity distributions are currently "
        "registered in the system ledger."
    )


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

st.markdown("### ")
st.markdown("---")
st.subheader("🔎 Triage Filter Selection Matrix")

filter_col1, filter_col2 = st.columns(2)


with filter_col1:
    selected_status = st.selectbox(
        "Filter Tickets By Operational Status:",
        ["All", "OPEN", "INVESTIGATING", "RESOLVED"],
        index=0,
    )


with filter_col2:
    selected_severity = st.selectbox(
        "Filter Tickets By Severity Classification:",
        ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
        index=0,
    )


# ---------------------------------------------------------------------------
# Incident Log Extraction
# ---------------------------------------------------------------------------

incidents_df = get_filtered_incidents_logs(
    status_filter=selected_status,
    severity_filter=selected_severity,
)


# ---------------------------------------------------------------------------
# Incident Data Grid
# ---------------------------------------------------------------------------

st.markdown("### ")

if not incidents_df.empty:

    render_standard_data_grid(
        df=incidents_df,
        columns_map=[
            "incident_id",
            "site_id",
            "equipment_id",
            "incident_type",
            "severity",
            "status",
            "start_time",
            "end_time",
            "description",
        ],
        empty_message="No incidents found.",
    )

else:

    st.info(
        "ℹ️ No operational incidents found matching the selected "
        "status and severity parameters."
    )