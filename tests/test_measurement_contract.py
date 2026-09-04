from datetime import datetime

from src.validation.measurement_contract import (
    validate_measurement,
)


def valid_measurement():
    """
    Fixture method generating a structurally clean, perfectly compliant 
    network measurement dictionary payload matching all contract expectations.
    """
    return {
        "source_record_id": "UG-TEST-001",
        "site_id": 1,
        "equipment_id": 1,
        "measured_at": datetime.now(),
        "traffic_mb": 1000,
        "latency_ms": 20,
        "packet_loss_pct": 0.5,
        "signal_strength_dbm": -60,
        "availability_pct": 99.9,
    }


def test_valid_measurement():
    """
    ARRANGE, ACT & ASSERT: Verifies that a standard, healthy network row 
    passes through our data contract firewall with absolute zero error tokens returned.
    """
    record = valid_measurement()
    errors = validate_measurement(record)
    assert errors == []


def test_negative_traffic_is_rejected():
    """
    ARRANGE, ACT & ASSERT: Verifies that an impossible negative traffic value 
    is caught, returning the explicit domain error message string token.
    """
    record = valid_measurement()
    record["traffic_mb"] = -100

    errors = validate_measurement(record)
    assert "traffic_mb must be >= 0" in errors


def test_negative_latency_is_rejected():
    """
    ARRANGE, ACT & ASSERT: Verifies that an anomalous negative latency value 
    is successfully flagged by the contract validation engine rules.
    """
    record = valid_measurement()
    record["latency_ms"] = -5

    errors = validate_measurement(record)
    assert "latency_ms must be >= 0" in errors
def test_invalid_packet_loss_is_rejected():
    """
    ARRANGE, ACT & ASSERT: Verifies that an impossible packet loss percentage (> 100%)
    is successfully caught and returns the exact domain error message token.
    """
    record = valid_measurement()
    record["packet_loss_pct"] = 120

    errors = validate_measurement(record)
    assert "packet_loss_pct must be between 0 and 100" in errors


def test_invalid_availability_is_rejected():
    """
    ARRANGE, ACT & ASSERT: Verifies that an out-of-bounds availability percentage (> 100%)
    is captured cleanly by the contract validation engine rules.
    """
    record = valid_measurement()
    record["availability_pct"] = 101

    errors = validate_measurement(record)
    assert "availability_pct must be between 0 and 100" in errors


def test_required_fields_are_checked():
    """
    ARRANGE, ACT & ASSERT: Enforces structural schema integrity by verifying that 
    the deletion of a required foreign key field triggers an immediate required error string.
    """
    record = valid_measurement()
    del record["site_id"]

    errors = validate_measurement(record)
    assert "site_id is required" in errors


def test_multiple_validation_errors():
    """
    ARRANGE, ACT & ASSERT: Verifies that our data contract framework evaluates rows comprehensively.
    If a record possesses multiple violations, the engine must return a complete error map array.
    """
    record = valid_measurement()
    record["traffic_mb"] = -100
    record["latency_ms"] = -20
    record["packet_loss_pct"] = 150

    errors = validate_measurement(record)
    assert len(errors) == 3
