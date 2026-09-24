import sys
from pathlib import Path
from sqlalchemy import text
from src.database import engine  # Reuses your centralized database connection engine pool [INDEX]

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents[0])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def start_pipeline_step(run_id: int, step_name: str) -> int:
    """
    Step Lifecycle Initialization: Creates a fresh database tracking record 
    marked as RUNNING and returns the newly generated step_id [INDEX].
    """
    query = text(
        """
        INSERT INTO pipeline_steps (run_id, step_name, status, started_at)
        VALUES (:run_id, :step_name, 'RUNNING', CURRENT_TIMESTAMP)
        RETURNING step_id;
        """
    )
    # Use engine.begin() for atomic, auto-committing database transaction blocks
    with engine.begin() as conn:
        step_id = conn.execute(
            query, 
            {"run_id": run_id, "step_name": step_name}
        ).scalar()
        return int(step_id)


def complete_pipeline_step(step_id: int, records_processed: int = 0) -> None:
    """
    Step Lifecycle Success State: Transitions an active step record to SUCCESS, 
    stamping completion times and actual row totals [INDEX].
    """
    query = text(
        """
        UPDATE pipeline_steps
        SET status = 'SUCCESS',
            completed_at = CURRENT_TIMESTAMP,
            records_processed = :records_processed
        WHERE step_id = :step_id;
        """
    )
    with engine.begin() as conn:
        conn.execute(
            query, 
            {"step_id": step_id, "records_processed": records_processed}
        )


def fail_pipeline_step(step_id: int, error_message: str) -> None:
    """
    Step Lifecycle Failure State: Transitions an active step record to FAILED, 
    stamping completion bounds and logging the unhandled exception text [INDEX].
    """
    query = text(
        """
        UPDATE pipeline_steps
        SET status = 'FAILED',
            completed_at = CURRENT_TIMESTAMP,
            error_message = :error_message
        WHERE step_id = :step_id;
        """
    )
    with engine.begin() as conn:
        conn.execute(
            query, 
            {"step_id": step_id, "error_message": error_message}
        )
