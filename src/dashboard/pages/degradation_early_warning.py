
"""Network degradation early-warning command center."""

import pandas as pd
import streamlit as st

from src.dashboard.degradation_data import load_degradation_assessments


st.title("Network Degradation Intelligence")
st.caption(
    "Measurement-level trend detection, explainable risk assessments, "
    "and site investigation."
)

st.warning(
    "Risk scores are heuristic indicators, not calibrated probabilities "
    "of network failure. Assessments depend on measurement coverage "
    "and freshness."
)

if st.button("Refresh assessment", type="primary"):
    st.rerun()

result = load_degradation_assessments()

if not result["ok"]:
    st.error(result["error"])
    st.caption(
        "No healthy status is inferred when measurement data cannot be loaded."
    )
    st.stop()

assessments = result["assessments"]

st.caption(
    f"Measurements evaluated: {result['measurement_count']:,} "
    f"across {len(assessments):,} sites."
)

if not assessments:
    st.info(
        "No site measurement history is available. Verify that "
        "silver_measurements contains records with valid site IDs and timestamps."
    )
    st.stop()


def count_status(status):
    return sum(item["status"] == status for item in assessments)


critical_count = count_status("CRITICAL")
warning_count = count_status("WARNING")
watch_count = count_status("WATCH")
stale_count = count_status("STALE_DATA")
insufficient_count = count_status("INSUFFICIENT_DATA")
healthy_count = count_status("HEALTHY")

col1, col2, col3 = st.columns(3)
col1.metric("Critical sites", critical_count)
col2.metric("Warning sites", warning_count)
col3.metric("Watch sites", watch_count)

col4, col5, col6 = st.columns(3)
col4.metric("Healthy sites", healthy_count)
col5.metric("Stale data", stale_count)
col6.metric("Insufficient history", insufficient_count)

st.divider()
st.subheader("Early-warning queue")

summary_rows = []

for item in assessments:
    summary_rows.append({
        "Site": item["site_name"],
        "Site ID": item["site_id"],
        "Status": item["status"],
        "Risk score": (
            item["risk_score"]
            if item["risk_score"] is not None
            else "N/A"
        ),
        "Measurements": item["observation_count"],
        "Deteriorating metrics": ", ".join(
            item.get("deteriorating_metrics", [])
        ),
        "Latest measurement (UTC)": item.get(
            "latest_measurement_at", "Unknown"
        ),
        "Data age (hours)": item.get("data_age_hours", "N/A"),
        "Assessment": item["reason"],
    })

summary = pd.DataFrame(summary_rows)

status_filter = st.multiselect(
    "Filter by assessment status",
    options=[
        "CRITICAL",
        "WARNING",
        "WATCH",
        "HEALTHY",
        "STALE_DATA",
        "INSUFFICIENT_DATA",
    ],
    default=[
        "CRITICAL",
        "WARNING",
        "WATCH",
        "STALE_DATA",
        "INSUFFICIENT_DATA",
    ],
)

filtered = summary[summary["Status"].isin(status_filter)]

st.dataframe(
    filtered,
    width="stretch",
    hide_index=True,
)

st.divider()
st.subheader("Site investigation")

selected_site_id = st.selectbox(
    "Select a site",
    options=[item["site_id"] for item in assessments],
    format_func=lambda site_id: next(
        (
            f"{item['site_name']} (ID {site_id}) — {item['status']}"
            for item in assessments
            if item["site_id"] == site_id
        ),
        f"Site {site_id}",
    ),
)

selected = next(
    item for item in assessments
    if item["site_id"] == selected_site_id
)

st.markdown(f"**Assessment:** {selected['status']}")
st.write(selected["reason"])

if selected["risk_score"] is not None:
    st.progress(
        selected["risk_score"] / 100,
        text=f"Heuristic risk score: {selected['risk_score']}/100",
    )
else:
    st.info("No risk score is issued for this assessment.")

if selected.get("latest_measurement_at"):
    st.caption(
        f"Latest observation: {selected['latest_measurement_at']} "
        "(UTC)"
    )

findings = selected.get("findings", [])

if findings:
    st.markdown("#### Metric evidence")

    findings_df = pd.DataFrame(findings)
    visible_columns = [
        "label",
        "baseline_median",
        "recent_median",
        "change_toward_degradation",
        "unit",
        "threshold_state",
        "deteriorating",
    ]

    st.dataframe(
        findings_df[visible_columns],
        width="stretch",
        hide_index=True,
    )

    for finding in findings:
        if (
            finding["threshold_state"] != "NORMAL"
            or finding["deteriorating"]
        ):
            st.markdown(f"**{finding['label']}**")
            st.write(finding["explanation"])
            st.caption(
                f"Threshold: {finding['threshold_state']} · "
                f"Deterioration detected: "
                f"{'Yes' if finding['deteriorating'] else 'No'}"
            )
else:
    st.info(
        "No comparable metric evidence is available for this site."
    )
