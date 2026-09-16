import json
import logging
from src.monitoring.alerts import generate_alerts
from src.monitoring.history import save_health_snapshot
from src.monitoring.report import generate_health_report

logging.basicConfig(level=logging.WARNING, format="%(asctime)s | %(levelname)s | %(message)s")


def main():
    """Central Orchestrator Runner: Runs system checks and saves a health history snapshot [INDEX]."""
    report = generate_health_report()
    alerts = generate_alerts(report)

    # Persist the health snapshot to the database ledger
    health_id = save_health_snapshot(report, alerts)

    output = {
        "health_id": health_id,
        "health": report,
        "alerts": alerts,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
