import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def get_reprocessing_summary():
    """
    Queries the database error table catalog to aggregate quarantine states.
    Returns a sorted list of dictionaries profiling data recovery metrics [INDEX].
    """
    logger.info("Extracting aggregate operational metrics from the quarantine reprocessing tracking hub...")
    
    query = text("""
        SELECT
            status,
            COUNT(*) AS records
        FROM quarantined_measurements
        GROUP BY status
        ORDER BY status;
    """)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    summary = [
        {
            "status": row[0],
            "records": row[1],
        }
        for row in rows
    ]
    
    logger.info(f"Successfully aggregated {len(summary)} discrete reprocessing lifecycles.")
    return summary
