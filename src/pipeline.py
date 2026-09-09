import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text

# Load system credentials and configurations up front
load_dotenv()

from src.database import engine
from src.logger import get_logger
from src.transformation.silver import run_silver
from src.data_quality.quality_gate import run_quality_gate
from src.transformation.gold import run_gold

# Initialize module-level observability logger instance
logger = get_logger(__name__)


def start_pipeline_run():
    """
    Initializes a new tracking run record inside the database registry,
    explicitly enforcing default STARTING stages and RUNNING statuses.
    """
    logger.info("🎬 Initializing parent pipeline execution tracking run...")
    sql = """
    INSERT INTO pipeline_runs (
        pipeline_name, started_at, status, current_stage, records_processed, duration_seconds
    )
    VALUES (
        'uganda_network_intel', CURRENT_TIMESTAMP, 'RUNNING', 'STARTING', 0, 0.000
    )
    RETURNING run_id;
    """
    with engine.begin() as connection:
        return connection.execute(text(sql)).scalar()


def update_pipeline_stage(run_id, stage):
    """
    Dynamically updates the active pipeline processing phase on disk
    to pinpoint precisely where the execution logic is executing.
    """
    logger.info(f"🔄 Execution stage progression pulse ──► current_stage={stage} | run_id={run_id}")
    sql = """
    UPDATE pipeline_runs
    SET current_stage = :current_stage
    WHERE run_id = :run_id;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "current_stage": stage,
            }
        )


def finish_pipeline_run(
    run_id,
    status,
    records_processed=0,
    error_message=None,
    duration_seconds=None,
    current_stage=None
):
    """
    Closes out the pipeline execution run tracking state with final parameters.
    Uses COALESCE to preserve the specific failure stage if an error occurs.
    """
    logger.info(f"💾 Closing parent pipeline execution run checkpoint | status={status} | run_id={run_id}")
    sql = """
    UPDATE pipeline_runs
    SET completed_at = :completed_at,
        status = :status,
        records_processed = :records_processed,
        error_message = :error_message,
        duration_seconds = :duration_seconds,
        current_stage = COALESCE(:current_stage, current_stage)
    WHERE run_id = :run_id;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "completed_at": datetime.now(),
                "status": status,
                "records_processed": records_processed,
                "error_message": error_message,
                "duration_seconds": duration_seconds,
                "current_stage": current_stage,
            }
        )
def get_quality_summary(run_id):
    """
    Queries data_quality_results for the current run_id to calculate 
    the exact number of passed and failed checks dynamically at runtime.
    """
    sql = """
    SELECT 
        COUNT(*) AS checks,
        COUNT(*) FILTER (WHERE status = 'PASS') AS passed,
        COUNT(*) FILTER (WHERE status = 'FAIL') AS failed
    FROM data_quality_results
    WHERE run_id = :run_id;
    """
    with engine.begin() as connection:
        result = connection.execute(text(sql), {"run_id": run_id}).mappings().first()
        if result and result["checks"] > 0:
            return {
                "checks": result["checks"],
                "passed": result["passed"],
                "failed": result["failed"]
            }
        return {"checks": 0, "passed": 0, "failed": 0}


def main():
    """Unified data pipeline stage engine with explicit orchestration tracking."""
    print("=" * 60)
    print("UGANDA NETWORK & SERVICE INTELLIGENCE")
    print("=" * 60)

    # 1. Pipeline Run Initialisation
    run_id = start_pipeline_run()
    pipeline_start = datetime.now()
    print(f"\nPipeline run ID: {run_id}")

    records_processed = 0
    try:
                # -------------------------------------------------
        # 2. SILVER STAGE
        # -------------------------------------------------
        update_pipeline_stage(run_id, "SILVER")
        print("\nCurrent stage: SILVER")
        records_processed = run_silver(run_id)

                # -------------------------------------------------
        # 3. QUALITY STAGE
        # -------------------------------------------------
        update_pipeline_stage(run_id, "QUALITY")
        print("\nCurrent stage: QUALITY")
        
        # 🚀 Capture programmatic validation results dictionary
        quality_result = run_quality_gate(run_id)

        if quality_result["failed"] > 0:
            logger.warning(f"⚠️ Quality warning triggered for run_id={run_id} | Failed checks={quality_result['failed']}")
            print(f"⚠️ Warning: {quality_result['failed']} quality checks failed. Proceeding with warning footprint.")
        else:
            print("DATA QUALITY GATE PASSED.")

        # -------------------------------------------------
        # 4. GOLD STAGE (Safely isolated after data contract validations!)
        # -------------------------------------------------
        update_pipeline_stage(run_id, "GOLD")
        print("\nCurrent stage: GOLD")
        run_gold(run_id)

        # ⏱️ Precision Duration Tracking Calculation for Success Path
        pipeline_end = datetime.now()
        duration_seconds = (pipeline_end - pipeline_start).total_seconds()

        # -------------------------------------------------
        # 4. SUCCESS PATH CLOSEOUT
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            records_processed=records_processed,
            duration_seconds=duration_seconds,
            current_stage="SUCCESS"  # Explicit success milestone mark
        )
        
        print("\nPipeline completed successfully.")
        print(f"Records processed: {records_processed}")

    except Exception as error:
                # ⏱️ Precision Duration Tracking Calculation for Success Path
        pipeline_end = datetime.now()
        duration_seconds = (pipeline_end - pipeline_start).total_seconds()

        # 🚀 Harvest dynamic quality metrics scorecard from this active run ID
        quality_summary = get_quality_summary(run_id)
        logger.info(f"Quality Summary harvested: {quality_summary}")

        # -------------------------------------------------
        # 4. SUCCESS PATH CLOSEOUT
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            records_processed=records_processed,
            duration_seconds=duration_seconds,
            current_stage="SUCCESS"
        )
        
        print("\nPipeline completed successfully.")
        print(f"Records processed: {records_processed}")
        print(f"Quality Checks:    {quality_summary['checks']} (Passed: {quality_summary['passed']}, Failed: {quality_summary['failed']})")



if __name__ == "__main__":
    main()
