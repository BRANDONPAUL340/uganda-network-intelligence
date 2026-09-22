PIPELINE_SLA_LIMIT_SECONDS = 60
FRESHNESS_SLA_LIMIT_HOURS = 1


def check_sla(runtime_seconds: float, limit_seconds: float) -> bool:
    """
    Return True when pipeline runtime is within the supplied SLA limit.
    """
    return runtime_seconds <= limit_seconds


def evaluate_pipeline_sla(runtime_seconds: float | None) -> str:
    """
    Evaluate pipeline runtime against the 60-second SLA.

    Returns:
        PASS: Runtime is within the SLA.
        BREACH: Runtime exceeds the SLA.
        UNKNOWN: Runtime is missing.
    """
    if runtime_seconds is None:
        return "UNKNOWN"

    return (
        "PASS"
        if check_sla(runtime_seconds, PIPELINE_SLA_LIMIT_SECONDS)
        else "BREACH"
    )


def evaluate_freshness(lag_hours: float | None) -> str:
    """
    Evaluate data freshness against the 1-hour freshness SLA.

    Returns:
        PASS: Data lag is within the freshness SLA.
        BREACH: Data lag exceeds the freshness SLA.
        UNKNOWN: Lag value is missing.
    """
    if lag_hours is None:
        return "UNKNOWN"

    return "PASS" if lag_hours <= FRESHNESS_SLA_LIMIT_HOURS else "BREACH"