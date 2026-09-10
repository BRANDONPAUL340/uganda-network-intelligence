from sqlalchemy import text
from src.database import engine


def start_stage(run_id, stage_name):
    """
    Initializes a new tracking phase record inside the stage ledger,
    explicitly passing a dynamic database timestamp value to protect
    against cross-environment not-null constraint exceptions.
    """
    query = text("""
        INSERT INTO pipeline_stage_runs (
            run_id,
            stage_name,
            status,
            started_at
        )
        VALUES (
            :run_id,
            :stage_name,
            'RUNNING',
            CURRENT_TIMESTAMP
        )
        RETURNING stage_run_id;
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "run_id": run_id,
                "stage_name": stage_name,
            },
        )
        return result.scalar_one()


def finish_stage(
    stage_run_id,
    status,
    records_processed=0,
    error_message=None,
):
    """
    Closes out the pipeline stage tracking phase record with explicit parameters,
    stamping the precise microsecond completion time indicator onto the database disk.
    """
    query = text("""
        UPDATE pipeline_stage_runs
        SET
            completed_at = CURRENT_TIMESTAMP,
            status = :status,
            error_message = :error_message
        WHERE stage_run_id = :stage_run_id;
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "stage_run_id": stage_run_id,
                "status": status,
                "error_message": error_message,
            },
        )
