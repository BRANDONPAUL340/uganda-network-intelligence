
"""Network degradation early-warning command center."""

import pandas as pd
import streamlit as st


from src.monitoring.root_cause_analysis import analyze_network_degradation
from src.dashboard.degradation_data import (
    load_degradation_assessments,
    load_dynamic_degradation_measurements,
)
from src.monitoring.degradation_early_warning import detect_degradation



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


st.divider()
st.subheader("Dynamic Thresholding & Early Warnings")
st.caption(
    "Site-level, same-hour historical baselines detect unusual readings. "
    "Static safety thresholds remain independent guardrails."
)

lookback_days = st.selectbox(
    "Historical baseline lookback",
    options=[30, 60, 90],
    index=2,
    format_func=lambda days: f"Last {days} days",
    key="dynamic_lookback_days",
)

try:
    dynamic_measurements = load_dynamic_degradation_measurements(
        days=lookback_days
    )
    dynamic_assessments = detect_degradation(dynamic_measurements)
except Exception:
    st.error(
        "Dynamic analysis could not load or process historical telemetry. "
        "The existing site assessments remain available above."
    )
    dynamic_assessments = pd.DataFrame()

if dynamic_assessments.empty:
    st.info(
        "No dynamic assessments are available for this lookback period. "
        "Check historical measurement coverage and timestamps."
    )
else:
    critical_dynamic = int(
        dynamic_assessments["severity"].eq("CRITICAL").sum()
    )
    warning_dynamic = int(
        dynamic_assessments["severity"].eq("WARNING").sum()
    )
    warming_up = int(
        dynamic_assessments["model_status"].eq("WARMING_UP").sum()
    )
    regression_count = int(
        dynamic_assessments["regression_detected"].fillna(False).sum()
    )

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Dynamic critical signals", critical_dynamic)
    metric_col2.metric("Dynamic warning signals", warning_dynamic)

    metric_col3, metric_col4 = st.columns(2)
    metric_col3.metric("Baselines warming up", warming_up)
    metric_col4.metric("Slow regressions detected", regression_count)

    st.markdown("#### Latest dynamic assessments")

    dynamic_filter = st.multiselect(
        "Filter dynamic severity",
        options=["CRITICAL", "WARNING", "INFO"],
        default=["CRITICAL", "WARNING"],
        key="dynamic_severity_filter",
    )

    latest_dynamic = (
        dynamic_assessments
        .sort_values("measured_at")
        .drop_duplicates(
            subset=["site_id", "metric"],
            keep="last",
        )
    )

    visible_dynamic = latest_dynamic[
        latest_dynamic["severity"].isin(dynamic_filter)
    ]

    dynamic_columns = [
        "site_name",
        "site_id",
        "measured_at",
        "metric",
        "observed",
        "expected",
        "robust_score",
        "severity",
        "model_status",
        "baseline_samples",
        "baseline_readiness",
        "seasonality_status",
        "reason",
    ]

    st.dataframe(
        visible_dynamic[dynamic_columns],
        width="stretch",
        hide_index=True,
    )

    st.markdown("#### Slow-regression signals")

    regression_rows = dynamic_assessments[
        dynamic_assessments["regression_detected"].fillna(False)
    ].copy()

    if regression_rows.empty:
        st.info(
            "No slow regressions met the detector's criteria "
            "for this lookback period."
        )
    else:
        regression_columns = [
            "site_name",
            "site_id",
            "metric",
            "observed",
            "expected",
            "regression_change_pct",
            "regression_reason",
        ]

        st.dataframe(
            regression_rows[regression_columns],
            width="stretch",
            hide_index=True,
        )

    st.caption(
        "Baselines require sufficient same-hour history. Robust scores "
        "may be unavailable when historical variation is zero. "
        "A warming-up baseline is not proof that a site is healthy."
    )
st.divider()
st.subheader("Root Cause Analysis")


diagnosis = analyze_network_degradation(selected)

st.markdown(f"**Summary:** {diagnosis['summary']}")
st.markdown(f"**Likely cause:** {diagnosis['likely_cause']}")
st.markdown(f"**Confidence:** {diagnosis['confidence']}")

st.markdown("**Supporting evidence**")
for evidence in diagnosis["evidence"]:
    st.write(f"- {evidence}")

st.markdown("**Recommended checks**")
for action in diagnosis["recommended_actions"]:
    st.write(f"- {action}")
