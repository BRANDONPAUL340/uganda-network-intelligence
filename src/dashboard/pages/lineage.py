
import streamlit as st

from src.dashboard.monitoring import (
    get_filtered_pipeline_runs,
    get_filtered_pipeline_lineage_logs,
    get_lineage_summary_metrics,
)
from src.dashboard.components.metrics import render_metric_card_grid
from src.dashboard.components.tables import render_standard_data_grid


# Standardized Header
st.title("🔗 Lineage")
st.caption(
    "Trace dataset lifecycles, data lineage paths, transformation steps, "
    "and affected row volumes."
)
st.markdown("---")


# ---------------------------------------------------------------------------
# Lineage Summary Metrics
# ---------------------------------------------------------------------------

with st.spinner("Aggregating structural data flow tracks..."):
    metrics = get_lineage_summary_metrics()

if (
    metrics["total_records"] == 0
    and metrics["unique_targets"] == 0
    and metrics["cumulative_rows"] == 0
):
    st.info("No lineage records are currently available.")

render_metric_card_grid(
    [
        {
            "label": "Total Lineage Links",
            "value": f"{metrics['total_records']:,}",
        },
        {
            "label": "Tracked Catalog Destinations",
            "value": f"{metrics['unique_targets']:,}",
        },
        {
            "label": "Cumulative Processed Volume",
            "value": f"{metrics['cumulative_rows']:,}",
        },
    ]
)


# ---------------------------------------------------------------------------
# Lineage History Filters
# ---------------------------------------------------------------------------

st.markdown("### ")
st.markdown("---")
st.subheader("🔍 Filter Data Lineage History")

all_runs_df = get_filtered_pipeline_runs(status_filter="All")

run_options = ["All"]

if not all_runs_df.empty:
    run_options.extend(
        [
            f"RUN-{int(rid):03d}"
            for rid in all_runs_df["run_id"].tolist()
        ]
    )

selected_run = st.selectbox(
    "Isolate Data Flow Trails By Parent Execution Run:",
    options=run_options,
    index=0,
)

lineage_df = get_filtered_pipeline_lineage_logs(
    run_id_filter=selected_run
)


# ---------------------------------------------------------------------------
# Lineage Records
# ---------------------------------------------------------------------------

st.markdown("### ")

if not lineage_df.empty:

    render_standard_data_grid(
        df=lineage_df,
        columns_map=[
            "lineage_id",
            "run_id",
            "source_table",
            "target_table",
            "records_processed",
            "created_at",
        ],
        empty_message=(
            "No operational lineage logs or dependency maps found "
            "matching the selected system metrics."
        ),
    )

    # -----------------------------------------------------------------------
    # Deep-Dive Transformation Inspector
    # -----------------------------------------------------------------------

    st.markdown("### ")
    st.markdown("---")
    st.subheader("🔬 Deep-Dive Data Transformation Inspector")

    available_ids = (
        lineage_df["lineage_id"]
        .astype(int)
        .tolist()
    )

    selected_lin_id = st.selectbox(
        "Select Active Lineage ID to Visualize Node Processing Flows:",
        options=available_ids,
        index=0,
    )

    flow = lineage_df[
        lineage_df["lineage_id"] == selected_lin_id
    ].iloc[0]

    st.markdown(
        f"### 📋 Dataset Dependency Profile: "
        f"Target Table `{flow['target_table']}`"
    )

    target_table = str(flow["target_table"])

    if "gold" in target_table.lower():
        upstream_node = "silver_network_metrics"
        source_stage = "SILVER SUITE LAYER"

    elif "silver" in target_table.lower():
        upstream_node = "bronze_network_records"
        source_stage = "BRONZE STAGING TANK"

    else:
        upstream_node = "external_network_source_stream"
        source_stage = "RAW INGESTION SUBSYSTEM"

    run_context = f"RUN-{int(flow['run_id']):03d}"

    st.success(
        f"**1. Upstream Feed Node ({source_stage}):** "
        f"`{upstream_node}`"
    )

    st.info(
        f"**⚡ 2. Active Transformation Driver Execution:** "
        f"`{run_context}` "
        f"(Processed Rows: `{int(flow['records_processed'] or 0):,}`)"
    )

    st.success(
        f"**🎯 3. Downstream Target Catalog Storage:** "
        f"`{target_table}`"
    )

else:
    st.info(
        "ℹ️ No operational lineage logs or dependency maps found "
        "matching the selected system metrics."
    )