import logging
from sqlalchemy import text
from src.database import engine
from src.monitoring.health import HealthStatus

logger = logging.getLogger(__name__)


def check_latest_pipeline_run():
    """
    Database State Monitor: Audits the pipeline_runs catalog to pull the 
    last recorded execution state and flags failures instantly [INDEX].
    """
    logger.info("Auditing latest macro-pipeline run status from database...")
    query = text("""
        SELECT status
        FROM pipeline_runs
        ORDER BY run_id DESC
        LIMIT 1;
    """)

    try:
        with engine.connect() as connection:
            status = connection.execute(query).scalar()
            
        logger.info(f"Raw database run token located: status=[{status}]")

        if status == "SUCCESS":
            return HealthStatus.HEALTHY
        if status == "FAILED":
            return HealthStatus.CRITICAL
        if status == "RUNNING":
            return HealthStatus.WARNING

        return HealthStatus.UNKNOWN
    except Exception as e:
        logger.error(f"Failed to check pipeline run logs due to exception: {str(e)}")
        return HealthStatus.CRITICAL


def check_latest_pipeline_stages():
    """
    Step-Level Stage Auditor: Analyzes the execution tokens for all steps 
    associated with the most recent pipeline run to find inner task failures [INDEX].
    """
    logger.info("Inspecting step-level stage statuses for the active run...")
    query = text("""
        SELECT status
        FROM pipeline_stage_runs
        WHERE run_id = (
            SELECT MAX(run_id)
            FROM pipeline_runs
        );
    """)

    try:
        with engine.connect() as connection:
            statuses = [row[0] for row in connection.execute(query).fetchall()]

        if not statuses:
            return HealthStatus.UNKNOWN

        if "FAILED" in statuses:
            return HealthStatus.CRITICAL
        if "RUNNING" in statuses:
            return HealthStatus.WARNING
        if all(status == "SUCCESS" for status in statuses):
            return HealthStatus.HEALTHY

        return HealthStatus.UNKNOWN
    except Exception as e:
        logger.error(f"Failed to extract inner stage run tracking tokens: {str(e)}")
        return HealthStatus.CRITICAL


def check_database_connection():
    """
    Infrastructure Connectivity Validator: Runs a lightweight diagnostic query
    to guarantee the database connection pool is operational [INDEX].
    """
    logger.info("Executing heartbeat select query to test database connection pool...")
    query = text("SELECT 1;")

    try:
        with engine.connect() as connection:
            connection.execute(query)
        logger.info("Database connection heartbeat checks passed perfectly.")
        return HealthStatus.HEALTHY
    except Exception as e:
        logger.critical(f"Database connectivity heartbeat check failed completely! Error: {str(e)}")
        return HealthStatus.CRITICAL
