import logging
from src.monitoring.checks import (
    check_database_connection,
    check_latest_pipeline_run,
    check_latest_pipeline_stages,
)
from src.monitoring.database_health import (
    check_database_size,
    check_dead_tuples,
)
from src.monitoring.health import combine_health_statuses

logger = logging.getLogger(__name__)


def generate_health_report():
    """
    Centralized Reporting Engine: Aggregates execution states, step logs, 
    and database performance metrics into a single unified tracking report [INDEX].
    """
    logger.info("Aggregates system components and query metrics for the centralized report...")

    checks = {
        "database": check_database_connection(),
        "database_size": check_database_size(),
        "dead_tuples": check_dead_tuples(),
        "latest_pipeline_run": check_latest_pipeline_run(),
        "pipeline_stages": check_latest_pipeline_stages(),
    }

    overall_status = combine_health_statuses(list(checks.values()))

    return {
        "overall_status": overall_status.value,
        "checks": {
            name: status.value
            for name, status in checks.items()
        },
    }
