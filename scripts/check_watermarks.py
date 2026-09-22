import sys
from pathlib import Path

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sqlalchemy import text
from src.database import engine  # Centralized database pooling configuration


def check_all_watermarks():
    """Queries the tracking metadata schema to dump streaming offsets per pipeline stage."""
    query = """
    SELECT pipeline_name, stage_name, source_name, last_raw_measurement_id, updated_at
    FROM processing_watermarks
    ORDER BY updated_at DESC;
    """
    with engine.connect() as conn:
        rows = conn.execute(text(query)).fetchall()
        for row in rows:
            print(dict(row._mapping))


if __name__ == "__main__":
    check_all_watermarks()