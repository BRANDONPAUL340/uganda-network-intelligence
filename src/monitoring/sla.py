from src.config import (
    MAX_DATA_FRESHNESS_DAYS,
    PIPELINE_SLA_SECONDS,
)


def evaluate_pipeline_sla(duration_seconds):
    """
    Programmatically determines if a completed pipeline execution
    run complied with or breached our duration target boundaries.
    """
    if duration_seconds is None:
        return "UNKNOWN"

    if duration_seconds <= PIPELINE_SLA_SECONDS:
        return "PASS"

    return "BREACH"


def evaluate_freshness(freshness_days):
    """
    Programmatically determines if the inbound staging data freshness
    falls within our required operational SLA timeline constraints.
    """
    if freshness_days is None:
        return "UNKNOWN"

    if freshness_days <= MAX_DATA_FRESHNESS_DAYS:
        return "PASS"

    return "BREACH"
