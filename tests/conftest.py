import pytest


@pytest.fixture
def quality_failure_v1_contract_mock():
    """
    6. Reusable V1 Contract Fixture: Provides a perfectly compliant Version 1.0.0
    data quality validation failure contract envelope blueprint [INDEX].
    """
    return {
        "event_id": "00000000-0000-0000-0000-000000000001",
        "event_type": "QUALITY_CHECK_FAILED",
        "event_version": 1,
        "run_id": 152,
        "event_time": "2026-09-30T16:00:00Z",
        "producer": "quality_engine",
        "payload": {
            "check_name": "duplicate_check",
            "status": "FAIL",
            "failed_records": 27,
            "message": "Duplicate measurements detected inside silver staging coordinates."
        }
    }


@pytest.fixture
def quality_failure_v2_contract_mock():
    """Provides a perfectly compliant graduated Version 2.0.0 data quality payload contract blueprint [INDEX]."""
    return {
        "event_id": "00000000-0000-0000-0000-000000000002",
        "event_type": "QUALITY_CHECK_FAILED",
        "event_version": 2,
        "run_id": 152,
        "event_time": "2026-09-30T16:00:00Z",
        "producer": "quality_engine",
        "payload": {
            "check": "duplicate_check",
            "severity": "HIGH",
            "error_description": "Duplicate measurements detected inside silver staging coordinates."
        }
    }
