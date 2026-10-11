import streamlit as st
import pandas as pd
from src.dashboard.monitoring import get_data_quality_summary_metrics, get_filtered_data_quality_results, get_filtered_pipeline_runs, get_data_quality_trends
from src.dashboard.components.metrics import render_metric_card_grid
from src.dashboard.components.tables import render_standard_data_grid
from src.dashboard.components.filters import render_dropdown_filter

st.title("✅ Data Quality")
st.caption("Monitor real-time data contract verifications, warning thresholds, and validation logs.")
st.markdown("---")

with st.spinner("Aggregating contract verification records..."):
    metrics = get_data_quality_summary_metrics()
    quality_trend_df = get_data_quality_trends()

if metrics["status"] == "ERROR":
    st.error("⚠️ Database Error: Unable to safely fetch quality verification summary logs from cluster.")

render_metric_card_grid([
    {"label": "✅ Checks Passed Successfully", "value": f"{metrics['pass']:,}"},
    {"label": "⚠️ Warning Threshold Exceptions", "value": f"{metrics['warn']:,}"},
    {"label": "🚨 Critical Quality Failures", "value": f"{metrics['fail']:,}"}
])

# 10 & 20. Quality Trend Line Graph
st.markdown("### ")
st.subheader("📈 Data Contract Compliance Trends Over Time")
if not quality_trend_df.empty:
    chart_data = quality_trend_df.copy()
    chart_data["eval_date"] = chart_data["eval_date"].astype(str)
    chart_data = chart_data.set_index("eval_date")
    st.line_chart(chart_data[["pass_count", "warn_count", "fail_count"]], color=["#2ecc71", "#f1c40f", "#e74c3c"])
else:
    st.info("ℹ️ No historical quality compliance trend series found on this cluster.")

st.markdown("### ")
st.markdown("---")
st.subheader("🔍 Filter Validation Reports Matrix")
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_status = render_dropdown_filter(label="Filter Logs By Quality Validation State:", options=["PASS", "WARN", "FAIL"], key="quality_state_filter_selector")

with filter_col2:
    all_runs_df = get_filtered_pipeline_runs(status_filter="All")
    run_options = []
    if not all_runs_df.empty:
        run_options = [f"RUN-{int(rid):03d}" for rid in all_runs_df["run_id"].tolist()]
    selected_run = render_dropdown_filter(label="Link Quality Results Directly To Parent Execution Run:", options=run_options, key="quality_run_id_filter_selector")

quality_df = get_filtered_data_quality_results(status_filter=selected_status, run_id_filter=selected_run)
st.markdown("### ")

if not quality_df.empty:
    quality_df["run_context"] = quality_df["run_id"].apply(lambda x: f"RUN-{int(x):03d}" if pd.notna(x) else "System Global")
    render_standard_data_grid(
    df=quality_df,
    columns_map=[
        "quality_result_id",
        "run_id",
        "table_name",
        "check_name",
        "check_type",
        "status",
        "records_checked",
        "records_failed",
        "failure_rate_pct",
        "severity",
        "checked_at",
    ],
    empty_message="No quality results found matching parameters."
)

st.markdown("### ")
st.markdown("---")
st.subheader("🔎 Verification Matrix")

if not quality_df.empty:
    verification_df = quality_df.copy()

    verification_df["run_context"] = verification_df["run_id"].apply(
        lambda x: f"RUN-{int(x):03d}" if pd.notna(x) else "System Global"
    )

    render_standard_data_grid(
        df=verification_df,
        columns_map=[
            "check_name",
            "run_context",
            "status",
            "measured_value",
            "records_checked",
            "records_failed",
            "severity",
            "evaluated_at",
        ],
        empty_message="No verification records are available for the selected filters."
    )
else:
    st.info("ℹ️ No verification records are available for the selected filters.")