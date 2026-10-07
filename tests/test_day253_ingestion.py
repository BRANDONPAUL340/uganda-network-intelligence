
from datetime import datetime

from src.dashboard.operations import (
    ingest_new_site,
    ingest_network_measurement,
    ingest_pipeline_incident,
)

def test_valid_site_accepted(db_connection):
    payload = {
        "name": "Day 253 Test Tower",
        "district": "Kampala",
        "region": "Central",
        "latitude": 0.3476,
        "longitude": 32.5825,
        "site_type": "Micro Cell",
        "status": "Active",
    }

    success, msg, site_id = ingest_new_site(
        db_connection,
        payload,
    )

    assert success is True
    assert site_id is not None
    assert "saved successfully" in msg


def test_duplicate_site_rejected(db_connection):
    payload = {
        "name": "Kampala Central Tower Hub",
        "district": "Kampala",
        "region": "Central",
        "latitude": 0.3476,
        "longitude": 32.5825,
        "site_type": "Macro Tower",
        "status": "Active",
    }

    # First insert establishes the record that the second
    # insertion must reject.
    first_success, _, first_site_id = ingest_new_site(
        db_connection,
        payload,
    )

    assert first_success is True
    assert first_site_id is not None

    # Second insert must be rejected as a duplicate.
    success, msg, site_id = ingest_new_site(
        db_connection,
        payload,
    )

    assert success is False
    assert site_id is None
    assert "already exists" in msg

# ============================================================
# MEASUREMENT TEST
# ============================================================

def test_invalid_measurement_rejected(db_connection):
    """
    Negative latency must be rejected by Pydantic validation.

    This test intentionally uses the real measurements contract.
    Database access should never be reached because the payload
    is invalid at the validation layer.
    """

    payload = {
        "equipment_id": 1,
        "site_id": 1,
        "measured_at": datetime.now(),

        "traffic_mb": 45.0,
        "latency_ms": -20.0,
        "packet_loss_pct": 0.0,
        "signal_strength_dbm": -70.0,
        "availability_pct": 99.0,
    }

    success, msg, measurement_id = ingest_network_measurement(
        db_connection,
        payload,
    )

    assert success is False
    assert measurement_id is None
    assert "latency_ms" in msg


# ============================================================
# INCIDENT TEST
# ============================================================

def test_incident_missing_resolution_timestamp_rejected(db_connection):
    """
    RESOLVED incidents must have an end_time.
    """

    payload = {
        "site_id": 1,
        "equipment_id": None,
        "incident_type": "Network Failure",
        "severity": "CRITICAL",
        "status": "RESOLVED",
        "start_time": datetime.now(),
        "end_time": None,
        "description": "Needs resolution timestamp",
    }

    success, msg, incident_id = ingest_pipeline_incident(
        db_connection,
        payload,
    )

    assert success is False
    assert incident_id is None
    assert "End Time" in msg