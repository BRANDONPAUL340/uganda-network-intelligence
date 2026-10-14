
"""Network Health Intelligence dashboard page."""

import pandas as pd
import streamlit as st

from src.dashboard.data import get_site_performance
from src.dashboard.network_health import assess_site


st.title("Network Health Intelligence")
st.caption(
    "Rank network sites by measured performance, identify threshold breaches, "
    "and guide operational investigations."
)
st.divider()

with st.spinner("Loading measured site performance..."):
    site_df = get_site_performance()

if site_df.empty:
    st.warning(
        "No site performance measurements are available. "
        "Check the database connection and ingestion pipeline."
    )
    st.stop()

required_columns = {
    "site_name",
    "measurement_count",
    "avg_latency_ms",
    "avg_packet_loss_pct",
    "avg_availability_pct",
}
missing_columns = required_columns.difference(site_df.columns)

if missing_columns:
    st.error(
        "The site performance query is missing expected columns: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()

health_df = site_df.copy()
assessments = health_df.apply(assess_site, axis=1, result_type="expand")
health_df = pd.concat([health_df, assessments], axis=1)

health_df["reasons_text"] = health_df["reasons"].apply(
    lambda items: "; ".join(items) if items else "No threshold breaches detected."
)
health_df["recommendations_text"] = health_df["recommendations"].apply(
    lambda items: "; ".join(items) if items else "No immediate action suggested."
)

status_order = {
    "Critical": 0,
    "Warning": 1,
    "Insufficient data": 2,
    "Healthy": 3,
}
health_df["risk_order"] = health_df["risk_status"].map(status_order)
health_df = health_df.sort_values(
    ["risk_order", "health_score"],
    ascending=[True, True],
    na_position="first",
).reset_index(drop=True)

critical_count = int((health_df["risk_status"] == "Critical").sum())
warning_count = int((health_df["risk_status"] == "Warning").sum())
healthy_count = int((health_df["risk_status"] == "Healthy").sum())
insufficient_count = int(
    (health_df["risk_status"] == "Insufficient data").sum()
)

metric_cols = st.columns(4)
metric_cols[0].metric("Sites assessed", f"{len(health_df):,}")
metric_cols[1].metric("Critical risk", f"{critical_count:,}")
metric_cols[2].metric("Warning", f"{warning_count:,}")
metric_cols[3].metric("Insufficient data", f"{insufficient_count:,}")

st.caption(
    "Scores are transparent threshold-based indicators, not carrier-certified SLA "
    "measurements. Sites with incomplete metrics are labelled Insufficient data."
)

st.subheader("Site risk ranking")

selected_statuses = st.multiselect(
    "Filter by health status",
    options=["Critical", "Warning", "Insufficient data", "Healthy"],
    default=["Critical", "Warning", "Insufficient data", "Healthy"],
)

filtered_df = health_df[
    health_df["risk_status"].isin(selected_statuses)
].copy()

display_columns = [
    column
    for column in [
        "site_name",
        "region",
        "district",
        "site_type",
        "health_score",
        "usable_metric_count",
        "risk_status",
        "measurement_count",
        "avg_latency_ms",
        "avg_packet_loss_pct",
        "avg_availability_pct",
    ]
    if column in filtered_df.columns
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True,
    column_config={
        "health_score": st.column_config.NumberColumn(
            "Health score",
            help="Heuristic score from 0 to 100; incomplete data may still have a provisional score.",
            format="%.0f",
        ),
        "usable_metric_count": st.column_config.NumberColumn(
            "Metrics available",
            help="Number of available performance metrics out of three.",
            format="%d/3",
        ),
        "avg_latency_ms": st.column_config.NumberColumn(
            "Avg latency (ms)", format="%.2f"
        ),
        "avg_packet_loss_pct": st.column_config.NumberColumn(
            "Avg packet loss (%)", format="%.2f"
        ),
        "avg_availability_pct": st.column_config.NumberColumn(
            "Avg availability (%)", format="%.2f"
        ),
        "measurement_count": st.column_config.NumberColumn(
            "Measurements", format="%d"
        ),
    },
)

csv_data = filtered_df[display_columns].to_csv(index=False).encode("utf-8")
st.download_button(
    "Export filtered site ranking (CSV)",
    data=csv_data,
    file_name="network_health_ranking.csv",
    mime="text/csv",
)

st.divider()
st.subheader("Investigation details")

if health_df.empty:
    st.info("No sites are available to inspect.")
else:
    site_options = health_df["site_name"].fillna("Unnamed site").astype(str).tolist()
    selected_index = st.selectbox(
        "Select a site",
        options=range(len(site_options)),
        format_func=lambda index: (
            f"{site_options[index]} — "
            f"{health_df.iloc[index]['risk_status']}"
        ),
    )

    selected_site = health_df.iloc[selected_index]

    detail_cols = st.columns(3)
    score = selected_site["health_score"]
    detail_cols[0].metric(
        "Health score",
        "Unavailable" if pd.isna(score) else f"{score:.0f}/100",
    )
    detail_cols[1].metric(
        "Metrics available",
        f"{int(selected_site['usable_metric_count'])}/3",
    )
    detail_cols[2].metric(
        "Measurements",
        int(selected_site["measurement_count"])
        if pd.notna(selected_site["measurement_count"])
        else "Unavailable",
    )

    st.markdown("**Why this site received its status**")
    for reason in selected_site["reasons"]:
        st.write(f"- {reason}")

    st.markdown("**Recommended investigation**")
    for recommendation in selected_site["recommendations"]:
        st.write(f"- {recommendation}")

st.caption(
    "Health score deductions: 35 points per critical metric breach and "
    "15 points per warning-only breach, bounded between 0 and 100. "
    "Configured thresholds are defined in src/config.py."
)
