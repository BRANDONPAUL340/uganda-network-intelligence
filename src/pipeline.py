from datetime import datetime

from sqlalchemy import text

from src.database import engine
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
    records_processed=0,
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
        records_processed = :records_processed,
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
                "records_processed": records_processed,
                "error_message": error_message,
            }
        )


def main():

    print("=" * 60)
    print("UGANDA NETWORK & SERVICE INTELLIGENCE")
    print("=" * 60)

    # -------------------------------------------------
    # 1. Start pipeline audit
    # -------------------------------------------------

    run_id = start_pipeline_run()

    print(f"\nPipeline run ID: {run_id}")

    try:

        # -------------------------------------------------
        # 2. Run Silver layer
        # -------------------------------------------------

        silver_result = run_silver()

        measurements_loaded = (
            silver_result["measurements_loaded"]
        )

        health_loaded = (
            silver_result["health_loaded"]
        )

        print(
            f"\nSilver measurements loaded: "
            f"{measurements_loaded}"
        )

        print(
            f"Silver health records loaded: "
            f"{health_loaded}"
        )

        # -------------------------------------------------
        # 3. Run Gold layer
        # -------------------------------------------------

        run_gold()

        # -------------------------------------------------
        # 4. Mark pipeline as successful
        # -------------------------------------------------

        finish_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            records_processed=measurements_loaded
        )

        print("\nPipeline completed successfully.")

    except Exception as error:

        # -------------------------------------------------
        # 5. Mark pipeline as failed
        # -------------------------------------------------

        finish_pipeline_run(
            run_id=run_id,
            status="FAILED",
            error_message=str(error)
        )

        print("\nPipeline failed.")
        print(f"Error: {error}")

        raise


if __name__ == "__main__":
    main()