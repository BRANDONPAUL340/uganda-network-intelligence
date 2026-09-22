import sys
from pathlib import Path

# Dynamic root path resolution hook
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.dashboard.health import check_dashboard_database, get_deployment_info


def main() -> int:
    print("Deployment verification")
    print("=" * 40)

    info = get_deployment_info()
    print(f"Version: {info['version']}")
    print(f"Environment: {info['environment']}")

    health = check_dashboard_database()
    print(f"Database status: {health.get('status')}")
    print(f"Heartbeat Message: {health.get('message')}")

    if health.get("status") != "HEALTHY":
        print("❌ Deployment verification FAILED")
        return 1

    print("✅ Deployment verification PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
