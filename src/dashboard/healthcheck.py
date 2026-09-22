import sys
from pathlib import Path

# dynamic project roadpath resolution hook
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.dashboard.health import check_dashboard_database


def main() -> int:
    """
    OCI Container Health Check Entrypoint: Evaluates application database 
    connectivity and maps the response to standard OS exit codes [INDEX].
    
    Exit Codes:
      0 -> SUCCESS / HEALTHY (Tells Podman the service is operational) [INDEX]
      1 -> FAILURE / UNHEALTHY (Tells Podman the container has degraded) [INDEX]
    """
    result = check_dashboard_database()

    # Output raw check telemetry parameters to standard stream for container logs
    print(f"Container health verification pass output: {result}")

    if result.get("status") == "HEALTHY":
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
