from src.monitoring.pipeline_alerts import check_pipeline_status
from src.monitoring.sla import create_sla_alert


def evaluate_pipeline(status: str, runtime_seconds: float, sla_seconds: float):
    """
    Central Alert Evaluation Hub: Combines status flags and execution speeds 
    to evaluate all active platform rules in a single step [INDEX].
    """
    alerts = []

    # 1. Audit pipeline processing status
    pipeline_alert = check_pipeline_status(status)
    if pipeline_alert:
        alerts.append(pipeline_alert)

    # 2. Audit SLA performance compliance boundaries
    sla_alert = create_sla_alert(runtime_seconds, sla_seconds)
    if sla_alert:
        alerts.append(sla_alert)

    return alerts
