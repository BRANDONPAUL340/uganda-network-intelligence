from sqlalchemy import text
from src.database import engine


def check_dashboard_database() -> dict:
    """
    Heartbeat Connectivity Checker: Runs a lightweight diagnostic pass 
    to verify database connection pool availability [INDEX].
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT 1")
            ).scalar()

        if result == 1:
            return {
                "status": "HEALTHY",
                "message": "Database connection is working",
            }

        return {
            "status": "WARNING",
            "message": "Unexpected database response",
        }

    except Exception as exc:
        return {
            "status": "CRITICAL",
            "message": str(exc),
        }


def get_dashboard_health() -> dict:
    """
    Consolidated Health Status Function: Combines frontend status 
    and backend database connectivity into a clean dictionary payload [INDEX].
    """
    database = check_dashboard_database()

    return {
        "application": "HEALTHY",
        "database": database["status"],
    }
