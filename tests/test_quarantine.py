from src.data_quality.measurements import (
    validate_record,
    get_validation_failure,
)


def test_invalid_packet_loss_is_rejected():
    """Asserts that an impossible out-of-bounds packet loss rate fails checks."""
    record = {
        "equipment_id": "1",
        "site_id": "1",
        "measured_at": "2026-09-03 10:00:00",
        "traffic_mb": "10000",
        "latency_ms": "20",
        "packet_loss_pct": "150",
        "signal_strength_dbm": "-60",
        "availability_pct": "99",
    }

    checks = validate_record(record)
    reason = get_validation_failure(checks)

    assert reason is not None
    assert "Packet loss must be between 0 and 100" in reason


def test_valid_record_has_no_failure():
    """Asserts that a standard, healthy network row passes with no error string."""
    record = {
        "equipment_id": "1",
        "site_id": "1",
        "measured_at": "2026-09-03 10:00:00",
        "traffic_mb": "10000",
        "latency_ms": "20",
        "packet_loss_pct": "1",
        "signal_strength_dbm": "-60",
        "availability_pct": "99",
    }

    checks = validate_record(record)
    reason = get_validation_failure(checks)

    assert reason is None
