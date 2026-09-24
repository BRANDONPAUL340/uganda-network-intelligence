import sys
from datetime import date, datetime, timezone
from pathlib import Path
import pandas as pd

# ==============================================================================
# 🌌 PROJECT PATHWAY RESOLUTION HOOK
# Resolves ModuleNotFoundError by anchoring the repository root to sys.path [INDEX].
# ==============================================================================
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import plotly.express as px
import streamlit as st

from src.config import PIPELINE_NAME
from src.dashboard.health import check_dashboard_database
from src.dashboard.version import DASHBOARD_VERSION
from src.dashboard.monitoring import get_open_alerts, get_recent_alerts
from src.monitoring.alert_metrics import (
    get_parameterized_alert_counts,
    get_parameterized_resolution_summary,
    get_parameterized_daily_trends,
    get_parameterized_alert_recurrence,
)
from src.dashboard.data import (
    check_database_connection,
    get_current_health,
    get_daily_health,
    get_database_activity,
    get_network_summary,
    get_pipeline_kpis,
    get_site_performance,
    get_stage_summary,
)

st.set_page_config(
    page_title="Uganda Network & Service Intelligence",
    page_icon="📡",
    layout="wide",
)

st.title("📡 Uganda Network & Service Intelligence Console")
st.caption(f"Operational Cockpit & Incident Analytics — Pipeline: {PIPELINE_NAME}")

if st.button("🔄 Refresh Application Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# ==============================================================================
# 🎛️ SIDEBAR INTERACTIVE CONTROL FILTERS & LIVE HEALTH INDICATOR
# ==============================================================================
st.sidebar.header("Dashboard Filters")
dashboard_health = check_dashboard_database()

if dashboard_health["status"] == "HEALTHY":
    st.sidebar.success("Database: Healthy")
else:
    st.sidebar.error("Database: Critical")

st.sidebar.caption(f"Dashboard version: {DASHBOARD_VERSION}")

try:
    all_sites_base = get_site_performance()
except Exception as exc:
    st.error(f"Unable to initialize filter datasets: {exc}")
    st.stop()

# 🌍 A. Geographic & Timeline Filters
regions = sorted(all_sites_base["region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region", ["All regions"] + regions)
region_filter = None if selected_region == "All regions" else selected_region

all_sites_base["measurement_date"] = pd.to_datetime(all_sites_base["measurement_date"]).dt.date
min_date = all_sites_base["measurement_date"].min() if not all_sites_base.empty else date.today()
max_date = all_sites_base["measurement_date"].max() if not all_sites_base.empty else date.today()

selected_dates = st.sidebar.date_input(
    "Operational analytical range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date, end_date = min_date, max_date

# FETCH METRIC DATA PANELS
try:
    kpis = get_pipeline_kpis()
    current_health = get_current_health()
    daily_health = get_daily_health()
    stage_summary = get_stage_summary()
    open_alerts = get_open_alerts()
    recent_alerts = get_recent_alerts()
    
    # Ingest dynamic parameterised analytics [INDEX]
    metrics_counts = get_parameterized_alert_counts(start_date, end_date)
    res_summary = get_parameterized_resolution_summary(start_date, end_date)
    trend_df = get_parameterized_daily_trends(start_date, end_date)
    recurrence_df = get_parameterized_alert_recurrence(start_date, end_date)
    
    network_summary = get_network_summary(region=region_filter, start_date=start_date, end_date=end_date)
    site_performance = get_site_performance(region=region_filter, start_date=start_date, end_date=end_date)
except Exception as exc:
    st.error(f"Unable to synchronize analytics data frames: {exc}")
    st.stop()


# ==============================================================================
# 🟢 CONTAINER SECTION 1: Pipeline Health Summary
# ==============================================================================
st.header("🟢 Core Pipeline Infrastructure Health")
if current_health.empty:
    st.warning("No pipeline health indicators available.")
else:
    pipeline_status = current_health["overall_status"].iloc[0]
    if pipeline_status == "HEALTHY":
        st.success(f"Pipeline Health Status: **{pipeline_status}** (⚡ Engine operating normally)")
    else:
        st.error(f"Pipeline Health Status: **{pipeline_status}** (⚠️ Active system delay tracked)")


# ==============================================================================
# 📊 CONTAINER SECTION 2: Labeled Operational Summary (Step 15)
# ==============================================================================
st.markdown("---")
st.header("📋 Incident Operational Summary")

col_op1, col_op2, col_op3, col_op4, col_op5 = st.columns(5)
col_op1.metric("Active Open Alerts", int(metrics_counts["open_alerts"]))
col_op2.metric("Alerts Triggered Today", int(metrics_counts["alerts_today"]))
col_op3.metric("Alerts Resolved Today", int(metrics_counts["resolved_today"]))
col_op4.metric("Avg Resolution Time", f"{res_summary['average_seconds']}m")
col_op5.metric("Median Resolution Time", f"{res_summary['median_seconds']}m")


# ==============================================================================
# 📉 CONTAINER SECTION 3: Alert Analytics & Trends (Step 12 & 13)
# ==============================================================================
st.markdown("---")
st.header("📉 Multi-Dimensional Alert Analytics")

col_an1, col_an2 = st.columns(2)

with col_an1:
    st.subheader("🗓️ Incident Volume Time-Series Trend")
    if trend_df.empty:
        st.info("No time-series data matches your chosen date window.")
    else:
        # Melt dataframe to plot created vs resolved comparisons natively
        melted_df = trend_df.melt(id_vars=["tracking_date"], value_vars=["created_count", "resolved_count"],
                                  var_name="Metric Type", value_name="Incident Count")
        fig_trend = px.line(melted_df, x="tracking_date", y="Incident Count", color="Metric Type",
                            markers=True, title="Alerts Created vs Alerts Resolved Over Time")
        st.plotly_chart(fig_trend, use_container_width=True)

with col_an2:
    st.subheader("🔄 Recurring Incident Distribution Check")
    if recurrence_df.empty:
        st.info("No recurring anomalies found inside this range window.")
    else:
        fig_rec = px.bar(recurrence_df, x="occurrences", y="alert_name", orientation="h",
                         title="Alert Volume Recurrence Density by Type",
                         labels={"occurrences": "Total Occurrence Frequency", "alert_name": "Alert Name Type"})
        st.plotly_chart(fig_rec, use_container_width=True)


# ==============================================================================
# 📡 CONTAINER SECTION 4: Network Metrics & Drill Downs
# ==============================================================================
st.markdown("---")
st.header("📊 Cellular Sites Performance Metrics")

if network_summary.empty or network_summary["total_sites"].iloc[0] is None:
    st.warning("No cellular tower performance values found within these filter targets.")
else:
    summary = network_summary.iloc[0]

    col_net1, col_net2, col_net3, col_net4 = st.columns(4)

    col_net1.metric(
        "Active Towers",
        int(summary["total_sites"] or 0)
    )

    col_net2.metric(
        "Total Ingested Data (MB)",
        f"{float(summary['avg_traffic_mb'] or 0):,.2f}"
    )

    col_net3.metric(
        "Avg Latency Metric",
        f"{float(summary['avg_latency_ms'] or 0):.2f}ms"
    )

    col_net4.metric(
        "Tower Link Availability",
        f"{float(summary['avg_availability_pct'] or 0):.2f}%"
    )
# ==============================================================================
# 🕵️‍♂️ CONTAINER SECTION: Incident Lineage Investigation & Traceability Center
# ==============================================================================
st.markdown("---")
st.header("🕵️‍♂️ Incident Lineage Investigation Center")

from src.dashboard.monitoring import (
    get_incident_complete_context,
    get_stage_details,
    get_run_lineage,
    get_current_processing_watermarks,
)

if not recent_alerts.empty:
    alert_choices = sorted(recent_alerts["alert_id"].dropna().unique().tolist(), reverse=True)
    selected_alert_id = st.selectbox("Select an Alert ID to map execution context & lineage roots", alert_choices)
    
    if selected_alert_id:
        # Fetch combined incident query context blocks [INDEX]
        incident_df = get_incident_complete_context(selected_alert_id)
        
        if not incident_df.empty:
            inc = incident_df.iloc[0]
            run_id = inc["run_id"]
            failed_stage = inc["stage_name"]
            
            # 17. Render Consolidated Incident Card Status Grid
            st.markdown(f"### 🚨 INCIDENT #{inc['alert_id']}")
            col_inc1, col_inc2 = st.columns(2)
            with col_inc1:
                st.info(f"**Alert Name:** `{inc['alert_name']}`\n\n**Message:** {inc['message']}")
                st.write(f"**Triggered At:** `{inc['triggered_at']}`")
                st.write(f"**Correlated Run ID:** `{int(run_id) if pd.notna(run_id) else 'N/A (Legacy/No Context)'}`")
            with col_inc2:
                st.write(f"**Incident Status:** `{inc['status']}`")
                st.write(f"**Severity Level:** `{inc['severity']}`")
                st.write(f"**Target Layer:** `{failed_stage or 'N/A'}`")
                if pd.notna(inc['resolved_at']):
                    st.write(f"**Resolved At:** `{inc['resolved_at']}`")
            
            # Conditionally expose execution metrics if a valid pipeline run is bound to the alert [INDEX]
            if pd.notna(run_id):
                run_id_int = int(run_id)
                
                st.markdown("---")
                st.subheader("⚙️ Correlated Pipeline Run Parameters")
                col_pr1, col_op2, col_pr3 = st.columns(3)
                col_pr1.metric("Pipeline Name", str(inc["pipeline_name"]))
                col_op2.metric("Execution Status", str(inc["pipeline_status"]))
                col_pr3.metric("Total Records Processed", f"{int(inc['records_processed'] or 0):,}")
                
                # 18. Add Stage Context Block Grids [INDEX]
                st.markdown("---")
                col_stg, col_wm = st.columns(2)
                
                with col_stg:
                    st.subheader("⏱️ Pipeline Stages Execution Breakdown")
                    stage_df = get_stage_details(run_id_int)
                    if stage_df.empty:
                        st.info("No sub-stage runs registered for this pipeline run instance.")
                    else:
                        st.dataframe(stage_df[["stage_name", "status", "duration_seconds", "started_at"]], 
                                     use_container_width=True, hide_index=True)
                
                with col_wm:
                    # 15. Connect Incremental Data Watermark Offsets [INDEX]
                    st.subheader("🎯 Active Processing Watermarks State")
                    watermarks_df = get_current_processing_watermarks()
                    if watermarks_df.empty:
                        st.info("No system processing watermarks logged inside tracking tables.")
                    else:
                        st.dataframe(watermarks_df[["stage_name", "source_name", "last_raw_measurement_id", "updated_at"]], 
                                     use_container_width=True, hide_index=True)
                
                # 19. Add Visual Lineage Trace Flow Diagrams
                st.markdown("---")
                st.subheader("🗺️ Data Lineage Ingestion Flow Trace")
                lineage_df = get_run_lineage(run_id_int)
                
                # Render metadata structural text diagram [INDEX]
                l_raw = "✅ measurements (RAW Vault Ingested)"
                l_silver = "🟢 SILVER (Cleaned & Deduplicated)" if failed_stage != "SILVER" else "❌ SILVER (Failed layer block)"
                l_gold = "🟡 GOLD (Analytical Reporting Layer)" if failed_stage not in ["SILVER", "GOLD"] else "⚪ GOLD (Not run due to failure)"
                
                st.text(f"""
                {l_raw}
                       │
                       ▼
                {l_silver}
                       │
                       ▼
                {l_gold}
                """)
                
                if not lineage_df.empty:
                    with st.expander("Expose Detailed Affected Table Record Rows"):
                        st.dataframe(lineage_df, use_container_width=True, hide_index=True)
            else:
                st.warning("ℹ️ This incident record does not contain active pipeline run-time correlation mapping context metadata fields.")
        else:
            st.error("Could not fetch trace parameters for the chosen alert token.")
else:
    st.info("No incidents logged in the history table ledger to investigate.")



# ==============================================================================
# 🔧 CONTAINER SECTION 5: Platform Engine Diagnostics Expander Logs
# ==============================================================================
st.markdown("---")
st.header("🔧 Platform Engine Diagnostics")
with st.expander("Active Database Activity Stream (pg_stat_activity)"):
    try:
        activity = get_database_activity()
        if activity.empty:
            st.info("No queries currently executing outside idle connection pools.")
        else:
            st.dataframe(activity, use_container_width=True, hide_index=True)
    except Exception as exc:
        st.warning(f"Could not extract process tracking parameters: {exc}")

st.divider()
st.caption("Uganda Network & Service Intelligence Data Platform — PostgreSQL 18 analytics view")
# ==============================================================================
# 🚨 OPERATIONS & MONITORING SECTION (Day 124 Enhanced UI Metrics Row)
# ==============================================================================
st.markdown("---")
st.header("🚨 Pipeline Operations & Monitoring Cockpit")

from src.dashboard.monitoring import (
    get_recent_runs,
    get_failed_runs,
    get_failed_steps,
    get_run_summary
)

# Fetch aggregate statistics data frames from database view models [INDEX]
try:
    pipeline_summary_df = get_run_summary()
    recent_runs_df = get_recent_runs(limit=10)
    failed_steps_df = get_failed_steps()
except Exception as exc:
    st.error(f"Unable to load active orchestration metrics logs: {exc}")
    st.stop()

# 7. Map summary data frames values into native Streamlit metric scorecards [INDEX]
if not pipeline_summary_df.empty:
    summary_row = pipeline_summary_df.iloc[0]
    total_runs = int(summary_row["total_runs"] or 0)
    successful_runs = int(summary_row["successful_runs"] or 0)
    failed_runs = int(summary_row["failed_runs"] or 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pipeline Runs", total_runs)
    with col2:
        st.metric("Successful Executions", successful_runs, delta="🟢 Operational")
    with col3:
        if failed_runs > 0:
            st.metric("Failed Executions", failed_runs, delta=f"⚠️ {failed_runs} Issues Tracked", delta_color="inverse")
        else:
            st.metric("Failed Executions", failed_runs, delta="✨ 0 Crashes")

# Render recent execution table logs for full operator traceability
st.markdown("### 📋 Recent Execution History Logs")
if recent_runs_df.empty:
    st.info("No active pipeline execution logs found on disk.")
else:
    st.dataframe(recent_runs_df, use_container_width=True, hide_index=True)

if not failed_steps_df.empty:
    st.markdown("### ❌ Fine-Grained Sub-Task Failures")
    st.dataframe(failed_steps_df, use_container_width=True, hide_index=True)
# ==============================================================================
# 📊 STEP PERFORMANCE VISUAL ANALYTICS (Day 124 Core Charting Blocks)
# ==============================================================================
from src.dashboard.monitoring import get_step_durations

try:
    step_data_df = get_step_durations()
except Exception as exc:
    st.error(f"Unable to load active stage execution metrics logs: {exc}")
    st.stop()

st.markdown("---")
st.subheader("⏱️ Micro-Stage Task Performance Analytics")

if step_data_df.empty:
    st.info("No sub-stage task runtime entries found to compute performance analytics.")
else:
    col_chart_left, col_chart_right = st.columns(2)
    
    with col_chart_left:
        # 11. Display polished, correct tabular data grid first for full engineering audits [INDEX]
        st.markdown("**Granular Task Execution Records**")
        st.dataframe(
            step_data_df[["run_id", "step_name", "status", "records_processed", "duration_seconds"]],
            use_container_width=True,
            hide_index=True
        )
        
    with col_chart_right:
        # 12. Display clean, aggregated average duration charts [INDEX]
        st.markdown("**Historical Average Stage Runtimes (Seconds)**")
        
        # Calculate mean execution lengths grouped strictly by step names [INDEX]
        avg_durations = (
            step_data_df.groupby("step_name")["duration_seconds"]
            .mean()
            .reset_index()
            .sort_values(by="duration_seconds", ascending=False)
        )
        
        # Render high-visibility bar graph without clunky visualization bloat [INDEX]
        st.bar_chart(
            data=avg_durations,
            x="step_name",
            y="duration_seconds",
            use_container_width=True
        )
# ==============================================================================
# 🕐 HIGH-WATERMARK EXECUTIONS & CONDITIONAL FAILURE DRILL-DOWNS (Day 124 Final)
# ==============================================================================
from src.dashboard.monitoring import get_last_successful_run, get_failed_steps

try:
    last_success_df = get_last_successful_run()
    failed_steps_df = get_failed_steps()
except Exception as exc:
    st.error(f"Unable to load active high-watermark analytics: {exc}")
    st.stop()

st.markdown("---")
col_obs_left, col_obs_right = st.columns(2)

with col_obs_left:
    # 13. Render the Last Successful Run status card panel
    st.subheader("🕐 Last Successful Run Baseline")
    if last_success_df.empty:
        st.info("No successful ingestion batch runs registered inside historical catalogs.")
    else:
        st.dataframe(
            last_success_df,
            use_container_width=True,
            hide_index=True
        )

with col_obs_right:
    # 14 & 15. Render Data-Responsive Failure Grids handling empty states gracefully
    st.subheader("⚠️ Failed Pipeline Steps Log")
    if failed_steps_df.empty:
        # Better UI Pattern: Clear success notification when zero rows match [INDEX]
        st.success("✅ **System Clean:** No failed pipeline sub-stage steps found on disk.")
    else:
        st.warning(f"🚨 **{len(failed_steps_df)} Faulty Sub-Task Executions Flagged!**")
        st.dataframe(
            failed_steps_df[["run_id", "step_name", "status", "error_message", "completed_at"]],
            use_container_width=True,
            hide_index=True
        )
