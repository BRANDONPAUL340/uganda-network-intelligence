import sys
from pathlib import Path

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sqlalchemy import text
from src.database import engine


def check_measurement_freshness():
    """
    Data Ingestion Lag Metric: Scans the high-volume base telemetry table 
    to retrieve the maximum event timestamp [INDEX].
    """
    query = """
    SELECT MAX(measured_at)
    FROM measurements;
    """

    with engine.connect() as conn:
        result = conn.execute(text(query)).scalar()

    return result
