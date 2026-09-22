import sys
from pathlib import Path

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sqlalchemy import text
from src.database import engine  # Use centralized production connection engine pool


def get_pipeline_status():
    """Queries the PostgreSQL audit catalog to retrieve details for the latest execution run [INDEX]."""
    query = """
    SELECT
        run_id,
        status,
        started_at,
        completed_at,
        records_processed
    FROM pipeline_runs
    ORDER BY run_id DESC
    LIMIT 1;
    """

    with engine.connect() as conn:
        row = conn.execute(text(query)).fetchone()

    if not row:
        return {"status": "UNKNOWN"}

    return dict(row._mapping)


def main():
    result = get_pipeline_status()

    print("=" * 50)
    print("UGANDA NETWORK PLATFORM STATUS DIAGNOSTIC")
    print("=" * 50)

    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
