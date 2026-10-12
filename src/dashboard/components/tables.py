"""
Uganda Network Intelligence Platform — Shared Table Component
Enforces structural contract validations, user-friendly labels, and null-safe badging [INDEX].
"""
import streamlit as st
import pandas as pd

# 10. Clean Production Column Display Name Mapping [INDEX]
COLUMNS_DISPLAY_MAP = {
    # Pipeline runs
    "run_id": "Run ID",
    "pipeline_name": "Pipeline Name",
    "current_stage": "Ingestion Stage",
    "status": "Execution Status",
    "started_at": "Started Timestamp",
    "completed_at": "Completed Timestamp",
    "duration": "Duration (s)",
    "duration_seconds": "Duration Seconds",

    # Data quality
    "quality_result_id": "Quality Result ID",
    "table_name": "Table Name",
    "check_name": "Quality Check",
    "check_type": "Check Type",
    "records_checked": "Records Checked",
    "records_failed": "Records Failed",
    "failure_rate_pct": "Failure Rate %",
    "details": "Details",
    "checked_at": "Checked Timestamp",
    "error_message": "Error Message",
    "severity": "Severity Classification",

    # Incidents
    "incident_id": "Incident Ticket ID",
    "site_id": "Site ID",
    "equipment_id": "Equipment ID",
    "incident_type": "Incident Type",
    "start_time": "Start Time",
    "end_time": "End Time",
    "description": "Description",

    # Events — retained only for compatibility with deferred event code
    "event_id": "Event Message ID",
    "event_type": "Message Type",
    "producer": "Origin Producer",
    "retry_count": "Retry Attempts",
    "processed_at": "Processed Timestamp",

    # Lineage
    "source_table": "Source Table",
    "target_table": "Target Destination Table",
    "records_processed": "Records Processed",
    "created_at": "Created Timestamp",
}

# Explicitly verified system lifecycle states [INDEX]
VALID_STATUS_CONTRACTS = {"SUCCESS", "FAILED", "RUNNING", "PASS", "WARN", "FAIL", "OPEN", "INVESTIGATING", "RESOLVED"}


def map_status_visual_token(val: str) -> str:
    """Status Validator Transformer: Converts raw enum keys into clean, readable badges [INDEX]."""
    if not val or pd.isna(val):
        return "⚪ UNKNOWN (NULL)"
        
    token = str(val).upper().strip()
    
    if token not in VALID_STATUS_CONTRACTS:
        return f"🔵 DRIFTED STATUS: {token}"
    
    if token in ["SUCCESS", "PASS", "RESOLVED", "COMPLETED"]:
        return f"🟢 {token}"
    elif token in ["RUNNING", "WARN", "INVESTIGATING", "RETRYING"]:
        return f"🟡 {token}"
    elif token in ["FAILED", "FAIL", "OPEN", "CRITICAL", "HIGH"]:
        return f"🔴 {token}"
        
    return f"🔵 {token}"


def validate_dataframe_schema_contract(df: pd.DataFrame, expected_columns: list):
    """Schema Validation Gate: Asserts that required structural columns exist [INDEX]."""
    if df is None or df.empty:
        return df
        
    missing_keys = set(expected_columns) - set(df.columns)
    if missing_keys:
        raise ValueError(f"Platform contract mismatch: Missing required columns: {missing_keys}")
        
    return df


def render_standard_data_grid(df: pd.DataFrame, columns_map: list, has_filters_applied: bool = False, empty_message: str = None):
    """Three-State Layout Grid: Formats timestamps and handles empty states safely [INDEX]."""
    # State 1: Explicit Database Failure Catch Barrier [INDEX]
    if df is None:
        st.error("⚠️ Component Error: Unable to safely load current logs from the cluster database layer.")
        return
        
    # State 2: Successful Query with Clean Zero-Row Filter Match [INDEX]
    if df.empty:
        if empty_message:
            st.info(empty_message)
        elif has_filters_applied:
            st.info('No operational records match the selected filters. Try broadening your criteria.')
        else:
            st.info('No operational records have been logged in this database context yet.')
        return

    processed_df = df.copy()
    
    # Null-Safe Fallback: Clean empty object references to avoid engine dropouts [INDEX]
    for col in processed_df.columns:
        if processed_df[col].dtype == object or str(processed_df[col].dtype) == "string":
            processed_df[col] = processed_df[col].fillna("—")
            
    # Format display timestamps without mutating database values [INDEX]
    for col in processed_df.columns:
        if any(token in str(col).lower() for token in ["_at", "time", "stamp", "created", "completed"]):
            processed_df[col] = processed_df[col].astype(str).str.slice(0, 19)
            processed_df[col] = processed_df[col].replace(["NaT", "nan", "None"], "—")
            
    if "duration_seconds" in processed_df.columns and "duration" not in processed_df.columns:
        processed_df["duration"] = processed_df["duration_seconds"].apply(
            lambda x: "Running..." if pd.isna(x) or str(x) == "nan" or x == "—" else f"{int(float(x))}s"
        )
        
    for col in processed_df.columns:
        if str(col).lower() in ["status", "severity"]:
            processed_df[col] = processed_df[col].apply(map_status_visual_token)
            
    rename_targets = {k: v for k, v in COLUMNS_DISPLAY_MAP.items() if k in processed_df.columns}
    processed_df = processed_df.rename(columns=rename_targets)
    
    ui_display_columns = [COLUMNS_DISPLAY_MAP[k] for k in columns_map if k in COLUMNS_DISPLAY_MAP and COLUMNS_DISPLAY_MAP[k] in processed_df.columns]
    if not ui_display_columns:
        ui_display_columns = list(processed_df.columns)
        
    # State 3: Render validated data grid [INDEX]
    st.dataframe(
           processed_df[ui_display_columns],
           width="stretch",
           hide_index=True
)
