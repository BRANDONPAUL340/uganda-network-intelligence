from datetime import datetime
import time

from sqlalchemy import text

from src.database import engine
from src.quality import run_quality_checks
from src.transformation.silver import run_silver
from src.transformation.gold import run_gold


PIPELINE_NAME = "uganda_network_intelligence"


def start_pipeline_run():
    """
    Create a new pipeline audit record.
    """

    sql = """
    INSERT INTO pipeline_runs (
        pipeline_name,
        started_at,
        status
    )

    VALUES (
        :pipeline_name,
        :started_at,
        'RUNNING'
    )

    RETURNING run_id;
    """

    with engine.begin() as connection:

        result = connection.execute(
            text(sql),
            {
                "pipeline_name": PIPELINE_NAME,
                "started_at": datetime.now(),
            }
        )

        return result.scalar()


def finish_pipeline_run(
    run_id,
    status,
    records_read=0,
    records_processed=0,
    records_rejected=0,
    duration_seconds=0,
    error_message=None
):
    """
    Update the pipeline audit record when the run finishes.
    """

    sql = """
    UPDATE pipeline_runs

    SET
        completed_at = :completed_at,
        status = :status,
        records_read = :records_read,
        records_processed = :records_processed,
        records_rejected = :records_rejected,
        duration_seconds = :duration_seconds,
        error_message = :error_message

    WHERE run_id = :run_id;
    """

    with engine.begin() as connection:

        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "completed_at": datetime.now(),
                "status": status,
                "records_read": records_read,
                "records_processed": records_processed,
                "records_rejected": records_rejected,
                "duration_seconds": duration_seconds,
                "error_message": error_message,
            }
        )


def get_measurement_count():
    """
    Return the total number of raw measurements.
    """

    sql = """
    SELECT COUNT(*)
    FROM measurements;
    """

    with engine.begin() as connection:

        result = connection.execute(text(sql))

        return result.scalar()


def main():

    print("=" * 60)
    print("UGANDA NETWORK & SERVICE INTELLIGENCE")
    print("=" * 60)

    # Start execution timer
    start_time = time.perf_counter()

    # Create audit record
    run_id = start_pipeline_run()

    print(f"\nPipeline run ID: {run_id}")

    # 📊 Dynamically collect raw volume metrics on startup
    records_read = get_measurement_count()
    records_processed = 0
    records_rejected = 0

    print(
        f"Records read from measurements: "
        f"{records_read}"
    )

    try:

        # -------------------------------------------------
        # 1. DATA QUALITY
        # -------------------------------------------------

        print("\nRunning data quality checks...")

        run_quality_checks()

        # -------------------------------------------------
        # 2. SILVER
        # -------------------------------------------------

        silver_result = run_silver()

        # Safe Fallback: Map either raw integer rows counts or dictionary outputs cleanly
        if isinstance(silver_result, dict):
            records_processed = silver_result.get("measurements_loaded", 0)
        else:
            records_processed = silver_result if silver_result is not None else 0

        print(
            f"\nRecords processed: "
            f"{records_processed}"
        )

        # -------------------------------------------------
        # 3. GOLD
        # -------------------------------------------------

        run_gold()

        # -------------------------------------------------
        # 4. SUCCESS
        # -------------------------------------------------

        duration = (
            time.perf_counter() - start_time
        )

        finish_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            records_read=records_read,
            records_processed=records_processed,
            records_rejected=records_rejected,
            duration_seconds=duration
        )

        print("\nPipeline completed successfully.")

        print(
            f"Execution time: "
            f"{duration:.3f} seconds"
        )

    except Exception as error:

        # -------------------------------------------------
        # 5. FAILURE
        # -------------------------------------------------

        duration = (
            time.perf_counter() - start_time
        )
        
        # Determine rejected rows count if a validation failure occurred inside raw
        if "Data quality checks failed" in str(error):
            records_rejected = records_read

        finish_pipeline_run(
            run_id=run_id,
            status="FAILED",
            records_read=records_read,
            records_processed=records_processed,
            records_rejected=records_rejected,
            duration_seconds=duration,
            error_message=str(error)
        )

        print("\nPipeline failed.")

        print(
            f"Execution time: "
            f"{duration:.3f} seconds"
        )

        print(f"Error: {error}")

        raise


if __name__ == "__main__":
    main()
