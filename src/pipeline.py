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
    """Initializes a new tracking run record inside the database registry."""
    sql = """
    INSERT INTO pipeline_runs (pipeline_name, status, records_processed, current_stage, duration_seconds)
    VALUES ('uganda_network_intel', 'RUNNING', 0, 'START', 0.000)
    RETURNING run_id;
    """
    with engine.begin() as connection:
        return connection.execute(text(sql)).scalar()


def update_pipeline_stage(run_id, stage):
    """Dynamically updates the active pipeline processing phase on disk."""
    sql = """
    UPDATE pipeline_runs
    SET current_stage = :stage
    WHERE run_id = :run_id;
    """
    with engine.begin() as connection:
        connection.execute(text(sql), {"run_id": run_id, "stage": stage})


def finish_pipeline_run(
    run_id,
    status,
    records_processed=0,
    error_message=None,
    duration_seconds=None,
):
    """Closes out the pipeline execution run tracking state with final parameters."""
    sql = """
    UPDATE pipeline_runs
    SET completed_at = CURRENT_TIMESTAMP,
        status = :status,
        records_processed = :records_processed,
        error_message = :error_message,
        duration_seconds = :duration_seconds,
        current_stage = :current_stage
    WHERE run_id = :run_id;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "status": status,
                "records_processed": records_processed,
                "error_message": error_message,
                "duration_seconds": duration_seconds,
                "current_stage": status,  # Match final status context
            }
        )


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
        print("\n[STAGE] SILVER")
        
        # 🚀 Capture actual row processing mutations from our return token
        records_processed = run_silver(run_id)

        # -------------------------------------------------
        # 3. QUALITY STAGE
        # -------------------------------------------------
        update_pipeline_stage(run_id, "QUALITY")
        print("\n[STAGE] QUALITY")
        run_quality_gate(run_id)

        # -------------------------------------------------
        # 4. GOLD STAGE
        # -------------------------------------------------
        update_pipeline_stage(run_id, "GOLD")
        print("\n[STAGE] GOLD")
        run_gold(run_id)

        # ⏱️ Precision Duration Tracking Calculation for Success Path
        pipeline_end = datetime.now()
        duration_seconds = (pipeline_end - pipeline_start).total_seconds()

        # -------------------------------------------------
        # 5. SUCCESS PATH CLOSEOUT
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            records_processed=records_processed,
            duration_seconds=duration_seconds,
        )
        
        print("\nPipeline completed successfully.")
        print(f"Records processed: {records_processed}")
        print(f"Duration:          {duration_seconds:.3f} seconds")

    except Exception as error:
        # ⏱️ Precision Duration Tracking Calculation for Failure Path
        pipeline_end = datetime.now()
        duration_seconds = (pipeline_end - pipeline_start).total_seconds()

        # -------------------------------------------------
        # 6. FAILURE PATH CLOSEOUT
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="FAILED",
            records_processed=0,
            error_message=str(error),
            duration_seconds=duration_seconds,
        )

        print("\nPipeline failed.")
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()
