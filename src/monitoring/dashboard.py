import sys
import os
from pathlib import Path

# ==============================================================================
# 🌌 SYSTEM ROADPATH RESOLUTION HOOK
# Resolves ModuleNotFoundError by explicitly anchoring the repository root to sys.path
# ==============================================================================
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from src.database import engine

# 1. Page Presentation Configurations
st.set_page_config(
    page_title="Uganda Network Intelligence — Operations Console",
    page_icon="🇺🇬",
    layout="wide"
)

st.title("🇺🇬 Uganda Network & Service Intelligence")
st.subheader("Data Platform Operations & Performance KPI Center")
st.markdown("---")

# Approved catalog visibility boundary rules
REPORTING_VIEWS = {
    "pipeline_kpis",
    "current_pipeline_health",
    "daily_pipeline_health",
    "pipeline_stage_summary"
}

@st.cache_data(ttl=10)
def load_view_data(view_name):
    """Safely extracts real-time metrics directly from our PostgreSQL reporting views."""
    if view_name not in REPORTING_VIEWS:
        raise ValueError(f"Unsupported reporting view target: {view_name}")
        
    with engine.connect() as conn:
        query = text(f"SELECT * FROM {view_name};")
        return pd.read_sql_query(query, conn)

try:
    # 2. Extract Metric Framework Data Streams
    df_kpis = load_view_data("pipeline_kpis")
    df_current_health = load_view_data("current_pipeline_health")
    df_daily_trend = load_view_data("daily_pipeline_health")
    df_stages = load_view_data("pipeline_stage_summary")

    # 3. TOP ROW: Real-Time Operational Telemetry State Banner
    if not df_current_health.empty:
        current = df_current_health.iloc[0]
        status = current["overall_status"]

        if status == "HEALTHY":
            st.success(f"🟢 **GLOBAL SYSTEM STATE: {status}** | Checked At: {current['checked_at']}")
        elif status == "WARNING":
            st.warning(f"🟡 **GLOBAL SYSTEM STATE: {status}** | Checked At: {current['checked_at']}")
        else:
            st.error(f"🔴 **GLOBAL SYSTEM STATE: {status}** | Checked At: {current['checked_at']}")

    st.markdown("### 📊 Macro Platform Performance KPIs")
    col1, col2, col3, col4 = st.columns(4)

    if not df_kpis.empty:
        kpi = df_kpis.iloc[0]

        col1.metric(
            label="Total Ingestion Runs",
            value=int(kpi["total_runs"])
        )
        col2.metric(
            label="Pipeline Success Rate",
            value=f"{kpi['pipeline_success_rate']}%"
        )
        col3.metric(
            label="Availability History",
            value=f"{kpi['healthy_percentage']}%"
        )
        col4.metric(
            label="Active Platform Alerts",
            value=int(kpi["total_alerts"]),
            delta=int(kpi["total_critical_alerts"]),
            delta_color="inverse"
        )

    st.markdown("---")

    # 4. BOTTOM ROW: Split Column Analytics View Grid
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### ⚙️ Micro-Stage Task Performance (SLA Summary)")

        if not df_stages.empty:
            stage_columns = [
                "stage_name",
                "total_executions",
                "success_rate",
                "average_duration_seconds",
                "total_records_read",
                "total_records_inserted",
                "total_records_rejected",
                "total_records_skipped",
                "total_records_processed"  # Fallback metric element compatibility tracking
            ]

            available_columns = [
                column for column in stage_columns if column in df_stages.columns
            ]

            st.dataframe(
                df_stages[available_columns],
                use_container_width=True,
                hide_index=True
            )

    with col_right:
        st.markdown("### 📅 Platform Availability & Alert Timeline Trends")

        if not df_daily_trend.empty:
            df_daily_trend["health_date"] = pd.to_datetime(df_daily_trend["health_date"])

            fig = px.line(
                df_daily_trend,
                x="health_date",
                y="healthy_percentage",
                title="Historical Availability Trend (%)",
                labels={
                    "health_date": "Timeline Date",
                    "healthy_percentage": "Availability (%)"
                },
                markers=True
            )

            fig.update_layout(yaxis_range=[0, 100])

            st.plotly_chart(
                fig,
                use_container_width=True
            )

except Exception as e:
    st.error("🚨 **Unable to sync Operations Console with backend storage container.**")
    st.info(
        "Ensure your database URL environment variables are active "
        "and targeted at the correct Podman PostgreSQL port (5433)."
    )
    st.exception(e)
