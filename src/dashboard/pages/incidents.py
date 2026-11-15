
import html

import pandas as pd
import streamlit as st

from src.dashboard.monitoring import (
    get_incidents_summary_metrics,
    get_filtered_incidents_logs,
    get_incidents_severity_distribution,
)
from src.monitoring.root_cause_analysis import analyze_incident


# ---------------------------------------------------------------------------
# Shared styling
# ---------------------------------------------------------------------------

st.html("""
<style>
.incident-hero {
    background: linear-gradient(120deg, #101f38 0%, #173b56 65%, #087e83 100%);
    padding: 30px 32px;
    border-radius: 16px;
    color: white;
    margin-bottom: 22px;
}
.incident-eyebrow {
    color: #70e0d0;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.incident-hero h1 {
    color: white;
    font-size: 30px;
    margin: 9px 0;
}
.incident-hero p {
    color: #d2e3ed;
    margin: 0;
    font-size: 14px;
}
.incident-kpi {
    background: #14243a;
    border: 1px solid #29445d;
    border-radius: 13px;
    padding: 19px;
    min-height: 112px;
}
.incident-kpi-label {
    color: #a9c1d2;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .7px;
}
.incident-kpi-value {
    color: #ffffff;
    font-size: 29px;
    font-weight: 750;
    margin-top: 10px;
}
.incident-section-note {
    color: #8da6b8;
    font-size: 13px;
    margin-top: -8px;
}
.incident-footer {
    border-top: 1px solid #29445d;
    margin-top: 30px;
    padding-top: 14px;
    color: #8da6b8;
    font-size: 12px;
}
</style>
""")


def safe_text(value, default="—"):
    if value is None or pd.isna(value):
        return default
    return str(value)


def safe_count(metrics, key):
    try:
        return f"{int(metrics.get(key, 0) or 0):,}"
    except (TypeError, ValueError):
        return "0"


def render_kpi(label, value):
    st.html(f"""
    <div class="incident-kpi">
        <div class="incident-kpi-label">{html.escape(label)}</div>
        <div class="incident-kpi-value">{html.escape(str(value))}</div>
    </div>
    """)


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------

st.html("""
<div class="incident-hero">
    <div class="incident-eyebrow">Operational Intelligence / Incident Centre</div>
    <h1>Incident Management</h1>
    <p>Monitor operational incidents, prioritize service risks,
    investigate root causes and support effective resolution.</p>
</div>
""")


# ---------------------------------------------------------------------------
# Incident summary
# ---------------------------------------------------------------------------

with st.spinner("Loading incident intelligence..."):
    metrics = get_incidents_summary_metrics()
    severity_df = get_incidents_severity_distribution()

if not isinstance(metrics, dict):
    metrics = {"error": "Incident summary could not be retrieved."}

if "error" in metrics:
    st.warning("Incident summary data is currently unavailable.")
    st.caption(str(metrics["error"]))

st.subheader("Operational Incident Overview")
st.markdown(
    '<div class="incident-section-note">'
    'A consolidated view of recorded incident activity and resolution.'
    '</div>',
    unsafe_allow_html=True,
)

kpi_columns = st.columns(4)

kpis = [
    ("Total incidents", safe_count(metrics, "total_incidents")),
    ("Open incidents", safe_count(metrics, "open_incidents")),
    ("Critical / high", safe_count(metrics, "critical_high_incidents")),
    ("Resolved incidents", safe_count(metrics, "resolved_incidents")),
]

for column, (label, value) in zip(kpi_columns, kpis):
    with column:
        render_kpi(label, value)


# ---------------------------------------------------------------------------
# Severity distribution
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Incident Severity Distribution")
st.markdown(
    '<div class="incident-section-note">'
    'Understand how recorded incidents are distributed across severity levels.'
    '</div>',
    unsafe_allow_html=True,
)

if isinstance(severity_df, pd.DataFrame) and not severity_df.empty:
    if {"severity", "incident_count"}.issubset(severity_df.columns):
        chart_data = severity_df[["severity", "incident_count"]].copy()
        chart_data["incident_count"] = pd.to_numeric(
            chart_data["incident_count"], errors="coerce"
        ).fillna(0)
        chart_data = chart_data.set_index("severity")

        st.bar_chart(
            chart_data,
            horizontal=True,
            height=260,
        )
    else:
        st.info("The severity distribution does not contain the expected fields.")
else:
    st.info("No incident severity distribution is currently available.")


# ---------------------------------------------------------------------------
# Incident filtering
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Incident Triage Workspace")
st.markdown(
    '<div class="incident-section-note">'
    'Filter incident records to focus on the operational issues requiring attention.'
    '</div>',
    unsafe_allow_html=True,
)

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_status = st.selectbox(
        "Operational status",
        ["All", "OPEN", "INVESTIGATING", "RESOLVED"],
        key="incident_status_filter",
    )

with filter_col2:
    selected_severity = st.selectbox(
        "Severity classification",
        ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
        key="incident_severity_filter",
    )


# ---------------------------------------------------------------------------
# Incident records
# ---------------------------------------------------------------------------

incidents_df = get_filtered_incidents_logs(
    status_filter=selected_status,
    severity_filter=selected_severity,
)

if incidents_df is None:
    incidents_df = pd.DataFrame()

st.subheader("Incident Register")

if not incidents_df.empty:
    preferred_columns = [
        "incident_id",
        "site_id",
        "equipment_id",
        "incident_type",
        "severity",
        "status",
        "start_time",
        "end_time",
        "description",
    ]

    display_columns = [
        column for column in preferred_columns
        if column in incidents_df.columns
    ]

    display_df = incidents_df[display_columns].copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=390,
    )

    csv_data = incidents_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download incident register",
        data=csv_data,
        file_name="incident_register.csv",
        mime="text/csv",
        use_container_width=False,
    )

else:
    st.info("No incidents match the selected filters.")


# ---------------------------------------------------------------------------
# Root cause analysis
# ---------------------------------------------------------------------------

st.divider()
st.subheader("Incident Root Cause Analysis")
st.markdown(
    '<div class="incident-section-note">'
    'Select an incident to examine its likely cause, supporting evidence '
    'and recommended investigation steps.'
    '</div>',
    unsafe_allow_html=True,
)

required_columns = [
    "incident_id",
    "incident_type",
    "description",
    "severity",
]

if incidents_df.empty:
    st.info("Incident records are required before root cause analysis can be performed.")

elif not all(column in incidents_df.columns for column in required_columns):
    st.warning("The incident records are missing fields required for root cause analysis.")

else:
    incident_options = incidents_df["incident_id"].tolist()

    selected_incident_id = st.selectbox(
        "Select an incident to investigate",
        options=incident_options,
        format_func=lambda incident_id: (
            f"Incident #{incident_id} — "
            f"{safe_text(
                incidents_df.loc[
                    incidents_df["incident_id"] == incident_id,
                    "incident_type"
                ].iloc[0]
            )}"
        ),
        key="incident_rca_selector",
    )

    incident_row = incidents_df[
        incidents_df["incident_id"] == selected_incident_id
    ].iloc[0]

    diagnosis = analyze_incident(
        incident_type=safe_text(incident_row["incident_type"], ""),
        description=safe_text(incident_row["description"], ""),
        severity=safe_text(incident_row["severity"], ""),
    )

    if isinstance(diagnosis, dict):
        summary_col, cause_col = st.columns(2)

        with summary_col:
            with st.container(border=True):
                st.markdown("**Incident summary**")
                st.write(diagnosis.get("summary", "No summary available."))

        with cause_col:
            with st.container(border=True):
                st.markdown("**Likely cause**")
                st.write(diagnosis.get("likely_cause", "No likely cause available."))

        with st.container(border=True):
            st.markdown("**Analysis confidence**")
            st.write(diagnosis.get("confidence", "Not specified"))

        evidence_col, actions_col = st.columns(2)

        with evidence_col:
            with st.container(border=True):
                st.markdown("**Supporting evidence**")
                for evidence in diagnosis.get("evidence", []):
                    st.markdown(f"- {evidence}")

        with actions_col:
            with st.container(border=True):
                st.markdown("**Recommended investigation checks**")
                for action in diagnosis.get("recommended_actions", []):
                    st.markdown(f"- {action}")
    else:
        st.warning("Root cause analysis did not return a valid result.")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.html("""
<div class="incident-footer">
    UGANDA NETWORK & SERVICE INTELLIGENCE
    <span style="float:right;">Incident Management</span>
</div>
""")
