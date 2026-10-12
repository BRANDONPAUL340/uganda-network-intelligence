import streamlit as st
import pandas as pd
from src.dashboard.monitoring import get_pipeline_summary_metrics, get_filtered_pipeline_runs, get_pipeline_run_steps_trace
from src.dashboard.components.metrics import render_metric_card_grid
from src.dashboard.components.tables import render_standard_data_grid, validate_dataframe_schema_contract
from src.dashboard.components.filters import render_dropdown_filter

st.title("🔄 Pipeline Runs")
st.caption("Monitor complete pipeline execution history, execution durations, and granular step processing traces.")
st.markdown("---")

# 18. Wrap summary metrics in a safe error containment boundary
metrics = get_pipeline_summary_metrics()

if metrics is None or metrics.get("status") == "ERROR":
    st.error("⚠️ Component Error: Unable to safely calculate pipeline metrics. Database unreachable.")
else:
    render_metric_card_grid([
        {"label": "Total Logged Executions", "value": f"{metrics['total_runs']:,}"},
        {"label": "Successful State Passes", "value": f"{metrics['success_runs']:,}"},
        {"label": "Failed Active Operations", "value": f"{metrics['failed_runs']:,}"}
    ])

st.markdown("### ")
st.markdown("---")

st.subheader("🔍 Filter Execution Logs Matrix")
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_status = render_dropdown_filter(
        label="Filter Logs By Pipeline Status Contract:",
        options=["SUCCESS", "FAILED", "RUNNING"],
        key="runs_status_filter_selector"
    )

with filter_col2:
    baseline_runs_df = get_filtered_pipeline_runs(status_filter="All", run_id_filter="All")
    run_options = []
    if baseline_runs_df is not None and not baseline_runs_df.empty:
        run_options = [f"RUN-{int(rid):03d}" for rid in baseline_runs_df["run_id"].tolist()]
        
    selected_run = render_dropdown_filter(
        label="Isolate History Directly By Specific Execution ID:",
        options=run_options,
        key="runs_id_filter_selector"
    )

# 18. Request rows from the business monitoring layer
runs_df = get_filtered_pipeline_runs(status_filter=selected_status, run_id_filter=selected_run)
st.write("DEBUG — Selected status:", repr(selected_status))
st.write("DEBUG — Selected run:", repr(selected_run))
st.write("DEBUG — Result type:", type(runs_df).__name__)
st.write("DEBUG — Result shape:", getattr(runs_df, "shape", None))

is_filtered = (selected_status != "All") or (selected_run != "All")

st.markdown("### ")

# 18. Three-State Verification Interface Routing Pass
if runs_df is None:
    st.error("⚠️ Component Error: Unable to safely load run logs. Please check database connectivity.")

elif runs_df.empty:
    render_standard_data_grid(
        df=runs_df,
        columns_map=["run_id", "pipeline_name", "status", "started_at"],
        has_filters_applied=is_filtered,
        empty_message="No pipeline runs match the selected filters."
    )
else:
    try:
        validated_runs_df = validate_dataframe_schema_contract(runs_df, ["run_id", "pipeline_name", "status", "started_at"])
        schema_error = False
    except Exception as exc:
        schema_error = True
        print(f"🔴 Schema validation exception: {exc}")
        
    if schema_error:
        st.error("⚠️ Component Error: Loaded run logs failed structure validation constraints.")
    else:
        st.subheader("📋 Ingestion Execution Logs Ledger")
        render_standard_data_grid(
            df=validated_runs_df,
            columns_map=["run_id", "pipeline_name", "status", "started_at"],
            has_filters_applied=is_filtered
        )
        
        st.markdown("### ")
        st.markdown("---")
        
        st.subheader("🔬 Deep-Dive Step Trace Inspector")
        available_ids = validated_runs_df["Run ID"].tolist() if "Run ID" in validated_runs_df.columns else validated_runs_df["run_id"].astype(int).tolist()
        
        selected_run_id = st.selectbox("Select Active Run ID to Audit Step Processing Tree:", options=available_ids, index=0)
        
        # Safe extraction locator pass
        lookup_col = "Run ID" if "Run ID" in validated_runs_df.columns else "run_id"
        run_meta = validated_runs_df[validated_runs_df[lookup_col] == selected_run_id].iloc[0]
        
        with st.expander(f"📄 View Granular Metadata Profile: Run #{selected_run_id}", expanded=True):
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.markdown(f"**Pipeline Variant:** `{run_meta.get('Pipeline Name', run_meta.get('pipeline_name', '—'))}`")
            with col_meta2:
                st.markdown(f"**Target Ingestion Stage:** `{run_meta.get('Ingestion Stage', run_meta.get('current_stage', '—'))}`")
            with col_meta3:
                st.markdown(f"**Execution Status:** `{run_meta.get('Execution Status', run_meta.get('status', '—'))}`")
                
            st.markdown("---")
            st.markdown("**Sub-step Chronological Process Logs:**")
            
            steps_df = get_pipeline_run_steps_trace(run_id=int(selected_run_id))
            
            if steps_df is None:
                st.error("⚠️ Localized Error: Unable to fetch processing sub-steps. Database connection lost.")
            elif not steps_df.empty:
                for _, row in steps_df.iterrows():
                    status_token = str(row.get("status", "⚪ PENDING")).upper().strip()
                    badge_icon = "🟢" if "SUCCESS" in status_token or "PASS" in status_token else "🔴" if "FAIL" in status_token else "🟡"
                    st.markdown(f"{badge_icon} **Component:** `{row.get('step_name', '—')}` ── Status: **{row.get('status', '—')}**")
            else:
                st.info(f"ℹ️ Selected execution Run #{selected_run_id} contains no recorded sub-task steps on disk.")
