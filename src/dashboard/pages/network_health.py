
"""Network Intelligence — Enterprise Network Health Dashboard."""

import html

import pandas as pd
import streamlit as st

from src.dashboard.data import get_site_performance
from src.dashboard.network_health import assess_site


# ---------------------------------------------------------
# SHARED PAGE DESIGN
# ---------------------------------------------------------

st.html("""
<style>
.network-page {
    color: #e5edf7;
}

.network-hero {
    background: linear-gradient(120deg, #101e35 0%, #163b50 65%, #087e83 100%);
    border: 1px solid rgba(96, 220, 211, .22);
    border-radius: 18px;
    padding: 30px 32px;
    margin: 4px 0 24px 0;
}

.network-eyebrow {
    color: #70e0d2;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.network-hero h1 {
    color: #ffffff;
    font-size: clamp(27px, 4vw, 38px);
    font-weight: 750;
    line-height: 1.15;
    margin: 0 0 12px 0;
}

.network-hero p {
    color: #d1e4ec;
    font-size: 15px;
    line-height: 1.65;
    max-width: 760px;
    margin: 0;
}

.network-section-label {
    color: #12a99b;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.7px;
    text-transform: uppercase;
    margin: 22px 0 5px 0;
}

.network-section-description {
    color: #8493a7;
    font-size: 13px;
    margin-bottom: 16px;
}

.network-kpi {
    background: linear-gradient(145deg, #14243a, #1b3046);
    border: 1px solid #29445a;
    border-radius: 14px;
    padding: 19px;
    min-height: 112px;
}

.network-kpi-label {
    color: #a6b8c9;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 13px;
}

.network-kpi-value {
    color: #ffffff;
    font-size: 29px;
    font-weight: 750;
    line-height: 1.1;
}

.network-kpi-note {
    color: #8fa6b9;
    font-size: 11px;
    margin-top: 8px;
}

.network-status {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 750;
    letter-spacing: .3px;
}

.network-status.critical {
    color: #ffb4b4;
    background: rgba(220, 53, 69, .16);
    border: 1px solid rgba(220, 53, 69, .35);
}

.network-status.warning {
    color: #ffd58b;
    background: rgba(230, 159, 45, .14);
    border: 1px solid rgba(230, 159, 45, .35);
}

.network-status.healthy {
    color: #8be0bd;
    background: rgba(28, 166, 116, .14);
    border: 1px solid rgba(28, 166, 116, .35);
}

.network-status.insufficient {
    color: #c2cbd5;
    background: rgba(130, 145, 160, .15);
    border: 1px solid rgba(130, 145, 160, .3);
}

.network-panel {
    background: rgba(22, 39, 57, .65);
    border: 1px solid #29445a;
    border-radius: 14px;
    padding: 19px;
    margin: 8px 0 16px 0;
}

.network-panel-title {
    color: #e9f1f8;
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 5px;
}

.network-panel-description {
    color: #8fa4b8;
    font-size: 12px;
}

.network-score {
    color: #ffffff;
    font-size: 34px;
    font-weight: 800;
}

.network-footer {
    color: #8294a7;
    font-size: 11px;
    text-align: center;
    padding: 18px 0 8px 0;
}
</style>
""")


def safe_number(value, decimals=2, suffix=""):
    if pd.isna(value):
        return "Unavailable"
    return f"{float(value):,.{decimals}f}{suffix}"


def escape_text(value):
    if pd.isna(value):
        return "Not recorded"
    return html.escape(str(value))


def render_kpi(label, value, note):
    st.html(f"""
    <div class="network-kpi">
        <div class="network-kpi-label">{html.escape(label)}</div>
        <div class="network-kpi-value">{html.escape(str(value))}</div>
        <div class="network-kpi-note">{html.escape(note)}</div>
    </div>
    """)


# ---------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------

st.html("""
<div class="network-hero">
    <div class="network-eyebrow">Network Intelligence / Performance</div>
    <h1>Network Health Intelligence</h1>
    <p>
        Monitor site performance, identify network risks and explore
        operational indicators through a unified network intelligence workspace.
    </p>
</div>
""")

# ---------------------------------------------------------
# LOAD EXISTING NETWORK DATA
# ---------------------------------------------------------

with st.spinner("Loading network performance intelligence..."):
    site_df = get_site_performance()

if site_df.empty:
    st.warning(
        "No site performance measurements are currently available. "
        "The dashboard cannot display a site assessment without recorded measurements."
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
        "The existing site performance query is missing expected columns: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()

# ---------------------------------------------------------
# ASSESS SITE HEALTH USING EXISTING LOGIC
# ---------------------------------------------------------

health_df = site_df.copy()

assessments = health_df.apply(
    assess_site,
    axis=1,
    result_type="expand",
)

health_df = pd.concat([health_df, assessments], axis=1)

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

critical_count = int(
    (health_df["risk_status"] == "Critical").sum()
)

warning_count = int(
    (health_df["risk_status"] == "Warning").sum()
)

healthy_count = int(
    (health_df["risk_status"] == "Healthy").sum()
)

insufficient_count = int(
    (health_df["risk_status"] == "Insufficient data").sum()
)

total_sites = len(health_df)

# ---------------------------------------------------------
# NETWORK PERFORMANCE SUMMARY
# ---------------------------------------------------------

st.html("""
<div class="network-section-label">Network overview</div>
<div class="network-section-description">
    A consolidated snapshot of measured site health and performance.
</div>
""")

metric_columns = st.columns(4)

with metric_columns[0]:
    render_kpi(
        "Sites assessed",
        f"{total_sites:,}",
        "Sites with returned measurements",
    )

with metric_columns[1]:
    render_kpi(
        "Critical risk",
        f"{critical_count:,}",
        "Sites requiring priority attention",
    )

with metric_columns[2]:
    render_kpi(
        "Warning",
        f"{warning_count:,}",
        "Sites with warning-level breaches",
    )

with metric_columns[3]:
    render_kpi(
        "Healthy sites",
        f"{healthy_count:,}",
        "Sites within configured thresholds",
    )

st.caption(
    f"{insufficient_count:,} site(s) have insufficient data for a complete "
    "health assessment."
)

# ---------------------------------------------------------
# NETWORK HEALTH DISTRIBUTION
# ---------------------------------------------------------

st.html("""
<div class="network-section-label">Network health distribution</div>
<div class="network-section-description">
    Distribution of sites across the existing threshold-based health classifications.
</div>
""")

distribution = pd.DataFrame({
    "Health status": [
        "Critical",
        "Warning",
        "Insufficient data",
        "Healthy",
    ],
    "Sites": [
        critical_count,
        warning_count,
        insufficient_count,
        healthy_count,
    ],
})

chart_col, summary_col = st.columns([1.6, 1])

with chart_col:
    st.bar_chart(
        distribution.set_index("Health status"),
        horizontal=True,
        height=250,
    )

with summary_col:
    st.html('<div class="network-panel">')
    st.markdown("**Health classification**")

    for status, count in [
        ("Critical", critical_count),
        ("Warning", warning_count),
        ("Insufficient data", insufficient_count),
        ("Healthy", healthy_count),
    ]:
        percentage = (count / total_sites * 100) if total_sites else 0
        st.write(f"**{status}** — {count} sites ({percentage:.1f}%)")

    st.html("</div>")

# ---------------------------------------------------------
# SITE RISK RANKING
# ---------------------------------------------------------

st.html("""
<div class="network-section-label">Site performance intelligence</div>
<div class="network-section-description">
    Compare site performance, review health scores and identify sites
    requiring investigation.
</div>
""")

filter_col, sort_col = st.columns([1.4, 1])

with filter_col:
    selected_statuses = st.multiselect(
        "Filter sites by health status",
        options=[
            "Critical",
            "Warning",
            "Insufficient data",
            "Healthy",
        ],
        default=[
            "Critical",
            "Warning",
            "Insufficient data",
            "Healthy",
        ],
        key="network_health_status_filter",
    )

with sort_col:
    sort_option = st.selectbox(
        "Rank sites by",
        options=[
            "Risk priority",
            "Health score",
            "Latency",
            "Packet loss",
            "Availability",
        ],
        key="network_health_sort",
    )

filtered_df = health_df[
    health_df["risk_status"].isin(selected_statuses)
].copy()

sort_columns = {
    "Risk priority": ("risk_order", True),
    "Health score": ("health_score", True),
    "Latency": ("avg_latency_ms", False),
    "Packet loss": ("avg_packet_loss_pct", False),
    "Availability": ("avg_availability_pct", True),
}

sort_column, ascending = sort_columns[sort_option]

filtered_df = filtered_df.sort_values(
    sort_column,
    ascending=ascending,
    na_position="last",
)

display_columns = [
    column
    for column in [
        "site_name",
        "region",
        "district",
        "site_type",
        "health_score",
        "risk_status",
        "measurement_count",
        "avg_latency_ms",
        "avg_packet_loss_pct",
        "avg_availability_pct",
    ]
    if column in filtered_df.columns
]

display_df = filtered_df[display_columns].copy()

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
    height=390,
    column_config={
        "site_name": st.column_config.TextColumn("Network site"),
        "region": st.column_config.TextColumn("Region"),
        "district": st.column_config.TextColumn("District"),
        "site_type": st.column_config.TextColumn("Site type"),
        "health_score": st.column_config.NumberColumn(
            "Health score",
            format="%.0f",
        ),
        "risk_status": st.column_config.TextColumn("Health status"),
        "measurement_count": st.column_config.NumberColumn(
            "Measurements",
            format="%d",
        ),
        "avg_latency_ms": st.column_config.NumberColumn(
            "Latency (ms)",
            format="%.2f",
        ),
        "avg_packet_loss_pct": st.column_config.NumberColumn(
            "Packet loss (%)",
            format="%.2f",
        ),
        "avg_availability_pct": st.column_config.NumberColumn(
            "Availability (%)",
            format="%.2f",
        ),
    },
)

st.caption(f"Displaying {len(filtered_df):,} of {total_sites:,} assessed sites.")

csv_data = filtered_df[display_columns].to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download site performance report",
    data=csv_data,
    file_name="network_health_ranking.csv",
    mime="text/csv",
    use_container_width=False,
)

# ---------------------------------------------------------
# SITE INVESTIGATION WORKSPACE
# ---------------------------------------------------------

st.divider()

st.html("""
<div class="network-section-label">Site investigation workspace</div>
<div class="network-section-description">
    Explore individual site measurements, health assessments and
    recommended investigation activities.
</div>
""")

if health_df.empty:
    st.info("No sites are available for investigation.")
else:
    site_options = health_df["site_name"].fillna(
        "Unnamed site"
    ).astype(str).tolist()

    selected_index = st.selectbox(
        "Choose a network site",
        options=range(len(site_options)),
        format_func=lambda index: (
            f"{site_options[index]} — "
            f"{health_df.iloc[index]['risk_status']}"
        ),
        key="network_health_selected_site",
    )

    selected_site = health_df.iloc[selected_index]

    status = str(selected_site["risk_status"])

    status_class = {
        "Critical": "critical",
        "Warning": "warning",
        "Healthy": "healthy",
        "Insufficient data": "insufficient",
    }.get(status, "insufficient")

    score = selected_site["health_score"]

    score_text = (
        "Unavailable"
        if pd.isna(score)
        else f"{float(score):.0f}/100"
    )

    site_name = escape_text(selected_site["site_name"])

    st.html(f"""
    <div class="network-panel">
        <div class="network-panel-description">SELECTED NETWORK SITE</div>
        <div class="network-panel-title" style="font-size:22px;margin-top:8px">
            {site_name}
        </div>
        <div style="margin-top:12px">
            <span class="network-status {status_class}">
                {html.escape(status.upper())}
            </span>
        </div>
    </div>
    """)

    detail_columns = st.columns(4)

    with detail_columns[0]:
        st.metric("Health score", score_text)

    with detail_columns[1]:
        st.metric(
            "Latency",
            safe_number(selected_site["avg_latency_ms"], 2, " ms"),
        )

    with detail_columns[2]:
        st.metric(
            "Packet loss",
            safe_number(selected_site["avg_packet_loss_pct"], 2, "%"),
        )

    with detail_columns[3]:
        st.metric(
            "Availability",
            safe_number(selected_site["avg_availability_pct"], 2, "%"),
        )

    location_columns = st.columns(3)

    with location_columns[0]:
        st.caption("REGION")
        st.write(escape_text(selected_site.get("region")))

    with location_columns[1]:
        st.caption("DISTRICT")
        st.write(escape_text(selected_site.get("district")))

    with location_columns[2]:
        st.caption("SITE TYPE")
        st.write(escape_text(selected_site.get("site_type")))

    st.divider()

    reasons_col, recommendations_col = st.columns(2)

    with reasons_col:
        st.markdown("#### Assessment findings")

        reasons = selected_site["reasons"]

        if reasons:
            for reason in reasons:
                st.markdown(f"- {reason}")
        else:
            st.info("No assessment findings are available.")

    with recommendations_col:
        st.markdown("#### Recommended actions")

        recommendations = selected_site["recommendations"]

        if recommendations:
            for recommendation in recommendations:
                st.markdown(f"- {recommendation}")
        else:
            st.info("No investigation recommendations are available.")

# ---------------------------------------------------------
# METHODOLOGY AND FOOTER
# ---------------------------------------------------------

with st.expander("Health scoring methodology"):
    st.write(
        "Health scores are transparent threshold-based indicators, "
        "not carrier-certified SLA measurements."
    )

    st.write(
        "Critical metric breaches deduct 35 points per affected metric. "
        "Warning-only breaches deduct 15 points. Scores are bounded "
        "between 0 and 100."
    )

    st.write(
        "Sites with incomplete metrics are classified as Insufficient data "
        "unless a critical or warning breach has already been identified. "
        "Interpret incomplete assessments with caution."
    )

    st.caption(
        "Configured thresholds are defined in src/config.py."
    )

st.html("""
<div class="network-footer">
    UGANDA NETWORK & SERVICE INTELLIGENCE PLATFORM
    &nbsp;|&nbsp; NETWORK HEALTH INTELLIGENCE
</div>
""")
