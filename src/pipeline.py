from datetime import datetime

from sqlalchemy import text

from src.database import engine
from src.transformation.silver import run_silver
from src.transformation.gold import run_gold


def start_pipeline_run():

    # 🛠️ Fixed: Changed start_time to started_at to match database schema mapping
    sql = """
    INSERT INTO pipeline_runs (
        pipeline_name,
        started_at,
        status
    )
    VALUES (
        'uganda_network_intelligence',
        :started_at,
        'RUNNING'
    )
    RETURNING run_id;
    """

    with engine.begin() as connection:
        result = connection.execute(
            text(sql),
            {"started_at": datetime.now()}
        )

        return result.scalar()


def finish_pipeline_run(run_id, status, records_processed=0, error_message=None):

    # 🛠️ Fixed: Changed end_time to completed_at to match database schema mapping
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
    print("UGANDA NETWORK & SERVICE INTELLIGENCE PIPELINE")
    print("=" * 60)

    run_id = start_pipeline_run()

    print(f"\nPipeline run ID: {run_id}")

    try:

        print("\nRunning SILVER transformations...")
        run_silver()

        print("\nRunning GOLD transformations...")
        run_gold()

        finish_pipeline_run(
            run_id,
            "SUCCESS"
        )

        print("\nPipeline completed successfully.")

    except Exception as error:

        finish_pipeline_run(
            run_id,
            "FAILED",
            error_message=str(error)
        )

        print("\nPipeline failed.")
        print(f"Error: {error}")

        raise


if __name__ == "__main__":
    main()
