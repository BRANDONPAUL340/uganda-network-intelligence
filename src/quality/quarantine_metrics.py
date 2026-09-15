import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def get_quarantine_summary():
    """
    Queries the database error table catalog to aggregate data contract anomalies.
    Returns a sorted list of dictionaries profiling data failure reasons [INDEX].
    """
    logger.info("Extracting structured analytics profile summaries from the quarantine vault...")
    
    query = text("""
        SELECT
            rejection_reason,
            COUNT(*) AS rejected_records
        FROM quarantined_measurements
        GROUP BY rejection_reason
        ORDER BY rejected_records DESC;
    """)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    summary = [
        {
            "rejection_reason": row[0],
            "rejected_records": row[1],
        }
        for row in rows
    ]
    
    logger.info(f"Successfully aggregated {len(summary)} discrete rejection metrics.")
    return summary
