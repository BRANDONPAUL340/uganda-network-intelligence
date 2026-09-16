import logging
from sqlalchemy import text
from src.database import engine
from src.monitoring.health import HealthStatus

logger = logging.getLogger(__name__)


def check_database_size():
    """
    Audits the total byte volume footprint of the data lakehouse database on disk [INDEX].
    """
    logger.info("Auditing database volumetric storage size footprint...")
    query = text("SELECT pg_database_size(current_database());")

    try:
        with engine.connect() as connection:
            size_bytes = connection.execute(query).scalar()
        
        if size_bytes is None:
            return HealthStatus.UNKNOWN
            
        logger.info(f"Database space audited: {size_bytes} bytes on disk.")
        return HealthStatus.HEALTHY
    except Exception as e:
        logger.error(f"Database size metric audit failed: {str(e)}")
        return HealthStatus.UNKNOWN


def check_dead_tuples():
    """
    Audits dead tuples inside the database table views [INDEX].
    Tracks dead rows without throwing false alerts, as minor bloat is normal [INDEX].
    """
    logger.info("Auditing live/dead tuple ratio balance indicators...")
    query = text("SELECT COALESCE(SUM(n_dead_tup), 0) FROM pg_stat_user_tables;")

    try:
        with engine.connect() as connection:
            dead_tuples = connection.execute(query).scalar()
            
        if dead_tuples is None:
            return HealthStatus.UNKNOWN

        logger.info(f"Database dead tuple scan complete. Total isolated dead rows: {dead_tuples}")
        return HealthStatus.HEALTHY
    except Exception as e:
        logger.error(f"Dead tuple statistic collector scan failed: {str(e)}")
        return HealthStatus.UNKNOWN
