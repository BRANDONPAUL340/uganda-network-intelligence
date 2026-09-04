from datetime import datetime


def validate_measurement(record):
    """
    Validates a single network telemetry record row against the project's formal data contract.
    Enforces strict mathematical bounds, field presences, and native python data types.

    Returns:
        list[str]: Array list containing explicit error tokens describing contract failures.
    """
    errors = []

    # 🛡️ 1. Required Field Contracts Check
    required_fields = [
        "source_record_id",
        "site_id",
        "equipment_id",
        "measured_at",
    ]

    for field in required_fields:
        value = record.get(field)
        if value is None or str(value).strip() == "":
            errors.append(f"{field} is required")

    # Helper method to safely typecast numeric cells for evaluation boundaries
    def safe_float(val):
        if val is None or str(val).strip() == "":
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    # 🛡️ 2. Domain-Aware Mathematical Boundary Contracts
    traffic_mb = safe_float(record.get("traffic_mb"))
    if record.get("traffic_mb") is not None and traffic_mb is None:
        errors.append("traffic_mb must be a numeric value")
    elif traffic_mb is not None and traffic_mb < 0:
        errors.append("traffic_mb must be >= 0")

    latency_ms = safe_float(record.get("latency_ms"))
    if record.get("latency_ms") is not None and latency_ms is None:
        errors.append("latency_ms must be a numeric value")
    elif latency_ms is not None and latency_ms < 0:
        errors.append("latency_ms must be >= 0")

    packet_loss = safe_float(record.get("packet_loss_pct"))
    if record.get("packet_loss_pct") is not None and packet_loss is None:
        errors.append("packet_loss_pct must be a numeric value")
    elif packet_loss is not None and not (0 <= packet_loss <= 100):
        errors.append("packet_loss_pct must be between 0 and 100")

    availability = safe_float(record.get("availability_pct"))
    if record.get("availability_pct") is not None and availability is None:
        errors.append("availability_pct must be a numeric value")
    elif availability is not None and not (0 <= availability <= 100):
        errors.append("availability_pct must be between 0 and 100")

    signal_strength = safe_float(record.get("signal_strength_dbm"))
    if record.get("signal_strength_dbm") is not None and signal_strength is None:
        errors.append("signal_strength_dbm must be a numeric value")
    elif signal_strength is not None and not (-150 <= signal_strength <= 0):
        errors.append("signal_strength_dbm must be between -150 and 0")

    # 🛡️ 3. Native Data Type Contracts
    measured_at = record.get("measured_at")
    if measured_at is not None and not isinstance(measured_at, datetime):
        errors.append("measured_at must be a datetime object")

    return errors
