import pytest
from src.monitoring.event_contract import validate_event_envelope_contract


@pytest.fixture
def clean_mock_v1_event():
    """Generates a perfectly compliant version 1.0.0 event envelope payload [INDEX]."""
    return {
        "event_id": "evt_20260928_8a4b2c89",
        "event_type": "QUALITY_CHECK_FAILED",
        "event_version": "1.0.0",
        "run_id": 161,
        "event_time": "2026-09-28T10:22:00Z",
        "producer": "quality_engine",
        "payload": {
            "check_name": "duplicate_records",
            "failed_records": 0
        }
    }


def test_compliant_envelope_passes_contract_validation(clean_mock_v1_event):
    """ARRANGE, ACT & ASSERT: Verifies a clean event passes safely without raising errors [INDEX]."""
    try:
        validate_event_envelope_contract(clean_mock_v1_event)
    except Exception as exc:
        pytest.fail(f"Compliant event payload raised an unexpected contract validation failure: {exc}")


def test_missing_field_raises_key_error(clean_mock_v1_event):
    """ARRANGE, ACT & ASSERT: Verifies that removing a required field triggers a clear KeyError [INDEX]."""
    del clean_mock_v1_event["producer"]
    with pytest.raises(KeyError):
        validate_event_envelope_contract(clean_mock_v1_event)


def test_invalid_run_id_raises_value_error(clean_mock_v1_event):
    """ARRANGE, ACT & ASSERT: Verifies that an invalid run_id is blocked with a ValueError [INDEX]."""
    clean_mock_v1_event["run_id"] = -999
    with pytest.raises(ValueError):
        validate_event_envelope_contract(clean_mock_v1_event)
