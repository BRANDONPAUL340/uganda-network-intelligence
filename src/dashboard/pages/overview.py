
"""Executive Overview - Uganda Network & Service Intelligence Platform."""

import sys

import pandas as pd
import streamlit as st

from src.dashboard.monitoring import (
    get_pipeline_summary_metrics,
    get_recent_pipeline_logs,
    get_pipeline_runs_time_series,
)
from src.dashboard.data import (
    get_network_summary,
    get_current_health,
    get_daily_health,
)
from src.dashboard.components.metrics import render_metric_card_grid
from src.dashboard.components.tables import render_standard_data_grid
from src.dashboard.components.charts import (
    apply_chart_theme,
    render_line_chart,
    render_bar_chart,
    CHART_COLORS,
)


# ---------------------------------------------------------------------------
# SHARED PRESENTATION
# ---------------------------------------------------------------------------

apply_chart_theme()

st.title("Executive Overview")
st.caption(
    "A consolidated view of network performance, service health "
    "and data-platform operations."
)

st.markdown(
    """
    <style>
    .overview-intro {
        padding: 19px 22px;
        margin: 12px 0 22px 0;
        border: 1px solid rgba(93, 224, 206, 0.22);
        border-radius: 14px;
        background: rgba(16, 42, 62, 0.72);
    }

    .overview-intro strong {
        color: #5de0ce;
        font-size: 14px;
    }

    .overview-intro p {
        color: #b6c8d9;
        font-size: 13px;
        line-height: 1.7;
        margin: 7px 0 0 0;
    }

    .overview-section-note {
        color: #9fb2c5;
        font-size: 13px;
        margin-top: -7px;
        margin-bottom: 15px;
    }

    .overview-status {
        padding: 15px 17px;
        border: 1px solid rgba(120, 163, 190, 0.2);
        border-radius: 12px;
        background: rgba(16, 35, 54, 0.72);
        margin-bottom: 10px;
    }

    .overview-status-label {
        color: #9fb2c5;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .overview-status-value {
        color: #f1f7ff;
        font-size: 18px;
        font-weight: 700;
        margin-top: 5px;
    }

    .overview-status-detail {
        color: #a9bdcf;
        font-size: 12px;
        margin-top: 5px;
        line-height: 1.5;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="overview-intro">
        <strong>National network and platform visibility</strong>
        <p>
            Review recorded network measurements, historical health
            indicators, pipeline execution outcomes and recent
            operational activity. Figures reflect data returned by
            the platform's existing monitoring queries.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# SAFE DATA RETRIEVAL
# ---------------------------------------------------------------------------

def load_dataframe(loader, description):
    """Retrieve a dataframe without allowing one failed query to stop the page."""
    try:
        result = loader()
        if isinstance(result, pd.DataFrame):
            return result
        return pd.DataFrame()
    except Exception as exc:
        st.warning(
            f"{description} is currently unavailable. "
            f"Technical detail: {type(exc).__name__}"
        )
        return pd.DataFrame()


def load_metrics():
    """Retrieve monitoring metrics and normalize the result."""
    try:
        result = get_pipeline_summary_metrics()
        if isinstance(result, dict):
            return result
        return {"status": "ERROR"}
    except Exception as exc:
        st.warning(
            "Pipeline monitoring metrics could not be retrieved. "
            f"Technical detail: {type(exc).__name__}"
        )
        return {"status": "ERROR"}


def display_metric(value, suffix="", decimals=2):
    """Format numeric measurements without inventing missing values."""
    if value is None or pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):,.{decimals}f}{suffix}"
    except (TypeError, ValueError):
        return "N/A"


def display_count(value):
    """Format count metrics safely."""
    if value is None or pd.isna(value):
        return "N/A"

    try:
        return f"{int(value):,}"
    except (TypeError, ValueError, OverflowError):
        return "N/A"


# ---------------------------------------------------------------------------
# RETRIEVE EXISTING PLATFORM DATA
# ---------------------------------------------------------------------------

with st.spinner("Retrieving available platform information..."):
    network_summary_df = load_dataframe(
        get_network_summary,
        "Network summary",
    )
    health_df = load_dataframe(
        get_current_health,
        "Current network health",
    )
    daily_health_df = load_dataframe(
        get_daily_health,
        "Daily network health history",
    )

    metrics = load_metrics()

    recent_runs_df = load_dataframe(
        lambda: get_recent_pipeline_logs(limit=5),
        "Recent pipeline runs",
    )
    trend_df = load_dataframe(
        get_pipeline_runs_time_series,
        "Pipeline execution history",
    )


# ---------------------------------------------------------------------------
# NETWORK PERFORMANCE
# ---------------------------------------------------------------------------

st.markdown("---")
st.header("Network Performance")
st.markdown(
    '<div class="overview-section-note">'
    'Recorded network measurements and current health classifications.'
    '</div>',
    unsafe_allow_html=True,
)

if not network_summary_df.empty:
    summary = network_summary_df.iloc[0]

    network_columns = st.columns(4)

    network_metrics = [
        (
            "Sites Reporting",
            display_metric(summary.get("total_sites"), decimals=0),
        ),
        (
            "Average Availability",
            display_metric(summary.get("avg_availability_pct"), "%"),
        ),
        (
            "Average Latency",
            display_metric(summary.get("avg_latency_ms"), " ms"),
        ),
        (
            "Average Packet Loss",
            display_metric(summary.get("avg_packet_loss_pct"), "%"),
        ),
    ]

    for column, (label, value) in zip(network_columns, network_metrics):
        with column:
            st.metric(label, value)

    st.caption(
        "Network averages are calculated from the measurements returned "
        "by the existing summary query. They may not represent every "
        "site equally."
    )
else:
    st.info(
        "Network summary measurements are unavailable. "
        "No network KPI values are being inferred."
    )


# ---------------------------------------------------------------------------
# CURRENT AND HISTORICAL NETWORK HEALTH
# ---------------------------------------------------------------------------

health_col, history_col = st.columns(2)

with health_col:
    st.subheader("Current Network Health")

    if (
        not health_df.empty
        and {"health_status", "record_count"}.issubset(health_df.columns)
    ):
        health_chart = health_df.set_index("health_status")

        render_bar_chart(
            health_chart[["record_count"]],
            color=CHART_COLORS["secondary"],
        )

        st.dataframe(
            health_df,
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No current network-health records are available.")

with history_col:
    st.subheader("Daily Network Health")

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

        chart_colors = [
            health_colors.get(status, CHART_COLORS["neutral"])
            for status in history_chart.columns
        ]

        render_line_chart(
            history_chart,
            color=chart_colors,
        )
    else:
        st.info("No daily network-health history is available.")


# ---------------------------------------------------------------------------
# PIPELINE AND INCIDENT SUMMARY
# ---------------------------------------------------------------------------

st.markdown("---")
st.header("Data Platform Operations")
st.markdown(
    '<div class="overview-section-note">'
    'Pipeline execution outcomes and recorded operational incidents.'
    '</div>',
    unsafe_allow_html=True,
)

metrics_available = metrics.get("status") == "HEALTHY"

if metrics_available:
    render_metric_card_grid([
        {
            "label": "Total Pipeline Runs",
            "value": display_count(metrics.get("total_runs")),
        },
        {
            "label": "Successful Runs",
            "value": display_count(metrics.get("success_runs")),
        },
        {
            "label": "Failed Runs",
            "value": display_count(metrics.get("failed_runs")),
            "delta_color": "inverse",
        },
        {
            "label": "Open Incidents",
            "value": display_count(metrics.get("open_incidents")),
        },
    ])
else:
    st.warning(
        "Pipeline and incident summary metrics are unavailable. "
        "The page will not display assumed or placeholder totals."
    )


# ---------------------------------------------------------------------------
# PIPELINE EXECUTION TRENDS
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Pipeline Execution Trends")

if (
    not trend_df.empty
    and {"run_date", "success_runs", "failed_runs"}.issubset(
        trend_df.columns
    )
):
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
    st.info("No historical pipeline execution trend data is available.")


# ---------------------------------------------------------------------------
# RECENT PIPELINE ACTIVITY
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Recent Pipeline Activity")

render_standard_data_grid(
    df=recent_runs_df,
    columns_map=[
        "run_id",
        "pipeline_name",
        "current_stage",
        "status",
        "started_at",
        "duration",
    ],
    empty_message="No recent pipeline execution records are available.",
)


# ---------------------------------------------------------------------------
# EVIDENCE-BASED MONITORING STATUS
# ---------------------------------------------------------------------------

st.markdown("---")
st.header("Monitoring Availability")

status_col, detail_col = st.columns(2)

with status_col:
    st.markdown(
        """
        <div class="overview-status">
            <div class="overview-status-label">
                Pipeline monitoring query
            </div>
        """,
        unsafe_allow_html=True,
    )

    if metrics_available:
        st.success("Monitoring metrics available")
    else:
        st.warning("Monitoring metrics unavailable")

    st.markdown("</div>", unsafe_allow_html=True)

with detail_col:
    st.markdown(
        """
        <div class="overview-status">
            <div class="overview-status-label">
                Dashboard runtime
            </div>
        """,
        unsafe_allow_html=True,
    )

    st.metric("Streamlit", st.__version__)
    st.caption(f"Python {sys.version.split()[0]}")

    st.markdown("</div>", unsafe_allow_html=True)

st.caption(
    "Monitoring availability reflects the result of the existing "
    "pipeline summary query. It is not a comprehensive health check "
    "of every ingestion worker, service or infrastructure component."
)
