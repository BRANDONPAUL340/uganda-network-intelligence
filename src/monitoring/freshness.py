from datetime import datetime, timezone
from sqlalchemy import text
from src.database import engine
from src.monitoring.alerts import Alert


def check_measurement_freshness():
    """Data Ingestion Lag Metric: Scans table files to find the maximum timestamp [INDEX]."""
    query = "SELECT MAX(measured_at) FROM measurements;"
    with engine.connect() as conn:
        return conn.execute(text(query)).scalar()


def create_freshness_alert(latest_timestamp, max_age_seconds: float) -> Alert | None:
    """
    Freshness Breach Detection: Compares the maximum data event timestamp against 
    current system clocks, alerting engineers if data updates drop behind schedule [INDEX].
    """
    if latest_timestamp is None:
        return Alert(
            name="data_freshness_unknown",
            severity="SEV2",
            message="No latest measurement timestamp was found inside database tables.",
        )

    now = datetime.now(timezone.utc)

    # Force standard UTC timestamp validation rules to prevent timezone bugs
    if latest_timestamp.tzinfo is None:
        latest_timestamp = latest_timestamp.replace(tzinfo=timezone.utc)

    age = (now - latest_timestamp).total_seconds()

    if age > max_age_seconds:
        return Alert(
            name="data_freshness_breach",
            severity="SEV3",
            message=(
                f"Latest data is {age:.0f}s old; "
                f"maximum allowed age is {max_age_seconds:.0f}s"
            ),
        )

    return None
