import sys
from pathlib import Path
from sqlalchemy import text
from src.database import engine

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def get_incident_traceability_context(alert_id: int) -> dict:
    """
    Unified Correlation Engine: Joins alert history with active pipeline runs, 
    SLA metrics, watermarks, and file lineage routes to map root-cause triggers [INDEX].
    """
    ctx = {"alert": None, "pipeline_run": None, "watermarks": [], "stage_runs": []}

    # 1. Fetch Alert Baseline Metadata
    alert_query = text("SELECT * FROM alert_history WHERE alert_id = :alert_id;")
    with engine.connect() as conn:
        alert_row = conn.execute(alert_query, {"alert_id": alert_id}).fetchone()
        if not alert_row:
            return ctx
        ctx["alert"] = dict(alert_row._mapping)

    run_id = ctx["alert"].get("run_id")
    
    # If this is a historical alert without mapping keys, exit early safely [INDEX]
    if not run_id:
        return ctx

    # 2. Extract Pipeline Run Metadata Parameters
    run_query = text("SELECT * FROM pipeline_runs WHERE run_id = :run_id;")
    # 3. Extract Stage Level Watermarks
    watermark_query = text("SELECT * FROM processing_watermarks WHERE pipeline_name = 'network_pipeline';")
    # 4. Extract Stage-specific Task Durations
    stage_query = text("SELECT * FROM pipeline_stage_runs WHERE run_id = :run_id ORDER BY started_at;")

    with engine.connect() as conn:
        run_row = conn.execute(run_query, {"run_id": run_id}).fetchone()
        if run_row:
            ctx["pipeline_run"] = dict(run_row._mapping)

        wm_rows = conn.execute(watermark_query).fetchall()
        ctx["watermarks"] = [dict(r._mapping) for r in wm_rows]

        st_rows = conn.execute(stage_query, {"run_id": run_id}).fetchall()
        ctx["stage_runs"] = [dict(r._mapping) for r in st_rows]

    return ctx
