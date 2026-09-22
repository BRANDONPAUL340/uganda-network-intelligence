import sys
from pathlib import Path

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.monitoring.evaluate import evaluate_pipeline


def main():
    # 🧪 Baseline Normal Testing Values
    status = "SUCCESS"
    runtime_seconds = 25
    sla_seconds = 60

    # 🔬 To simulate an artificial failure condition, temporarily swap to:
    # status = "FAILED"
    # runtime_seconds = 120

    alerts = evaluate_pipeline(
        status=status,
        runtime_seconds=runtime_seconds,
        sla_seconds=sla_seconds,
    )

    print("=" * 50)
    print("UGANDA NETWORK INTELLIGENCE ALERT CHECK")
    print("=" * 50)

    if not alerts:
        print("STATUS: OK")
        return

    print(f"ALERTS DETECTED: {len(alerts)}")

    for alert in alerts:
        print()
        print(f"Name: {alert.name}")
        print(f"Severity: {alert.severity}")
        print(f"Message: {alert.message}")


if __name__ == "__main__":
    main()
