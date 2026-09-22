import logging
from src.monitoring.health import HealthStatus

logger = logging.getLogger(__name__)


def generate_alerts(report):
    """
    Decoupled Alert Generator: Sweeps the operational checks report grid 
    and translates any WARNING or CRITICAL state codes into standard actionable alert logs [INDEX].
    """
    alerts = []
    checks = report.get("checks", {})

    logger.info(f"Parsing health check matrices for alerts. Total items scanned: {len(checks)}")

    for name, status in checks.items():
        if status == HealthStatus.CRITICAL.value:
            alerts.append({
                "severity": "CRITICAL",
                "check": name,
                "message": f"CRITICAL ALERT: Component [{name}] requires immediate production attention!",
            })
            logger.warning(f"Routed CRITICAL alert for component: {name}")

        elif status == HealthStatus.WARNING.value:
            alerts.append({
                "severity": "WARNING",
                "check": name,
                "message": f"WARNING ALERT: Component [{name}] requires operational investigation.",
            })
            logger.info(f"Routed WARNING alert for component: {name}")

    logger.info(f"Alert parsing complete. Operational items triggered: {len(alerts)}")
    return alerts
from dataclasses import dataclass


@dataclass
class Alert:
    name: str
    severity: str
    message: str
    triggered: bool = True


def create_alert(name: str, severity: str, message: str) -> Alert:
    """ Programmatic constructor utility to build unified system alerts [INDEX]. """
    return Alert(name=name, severity=severity, message=message)

