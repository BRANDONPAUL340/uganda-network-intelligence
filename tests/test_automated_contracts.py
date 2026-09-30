"""
Uganda Network Intelligence Platform — Pre-Deployment Contract Verification Suite
Asserts structural rules and backward compatibility before system code changes are deployed [INDEX].
"""
import pytest
from src.monitoring.event_contract import validate_event
from src.monitoring.event_store import handle_quality_failure_event

# ==============================================================================
# 🎯 TIER 1: PRODUCER-SIDE CONTRACT FIREWALL TESTS
# ==============================================================================

def test_producer_v1_output_satisfies_envelope_and_payload_contracts(quality_failure_v1_contract_mock):
    """Test 7: Asserts that the code's version 1 output satisfies all layout guidelines [INDEX]."""
    result = validate_event(quality_failure_v1_contract_mock)
    assert result["valid"] is True, f"Contract broken: {result['errors']}"


def test_producer_v2_output_satisfies_graduated_contracts(quality_failure_v2_contract_mock):
    """Test 10: Asserts that version 2 output satisfies the refactored layout [INDEX]."""
    result = validate_event(quality_failure_v2_contract_mock)
    assert result["valid"] is True, f"Contract broken: {result['errors']}"


def test_quality_failure_requires_check_name(quality_failure_v1_contract_mock):
    """Test 8: Asserts that dropping a required payload key fails validation instantly [INDEX]."""
    event = quality_failure_v1_contract_mock.copy()
    event["payload"] = event["payload"].copy()
    del event["payload"]["check_name"]
    
    result = validate_event(event)
    assert result["valid"] is False


def test_failed_records_must_be_integer(quality_failure_v1_contract_mock):
    """Test 9: Asserts that passing an invalid data type (e.g., string count) triggers a failure [INDEX]."""
    event = quality_failure_v1_contract_mock.copy()
    event["payload"] = event["payload"].copy()
    event["payload"]["failed_records"] = "27"  # Should be int [INDEX]
    
    result = validate_event(event)
    assert result["valid"] is False


def test_unknown_event_version_rejected(quality_failure_v1_contract_mock):
    """Test 11: Asserts that arbitrary out-of-bounds versions are blocked cleanly [INDEX]."""
    event = quality_failure_v1_contract_mock.copy()
    event["event_version"] = 999
    
    result = validate_event(event)
    assert result["valid"] is False


# ==============================================================================
# 🎯 TIER 2: CONSUMER-SIDE BACKWARD COMPATIBILITY TESTS
# ==============================================================================

class MockDbConnection:
    """Mock connection to satisfy handler function interfaces."""
    pass


# Test 12 & 13: Parameterise fixture lookups to guarantee backward-compatible processing loops [INDEX]
@pytest.mark.parametrize(
    "event_fixture_name",
    [
        "quality_failure_v1_contract_mock",
        "quality_failure_v2_contract_mock",
    ],
)
def test_consumer_handlers_maintain_backward_compatibility_across_versions(request, event_fixture_name):
    """
    Test 12 & 13: Backward Compatibility Test: Verifies that the active consumer logic 
    can safely parse and process every supported historical event version contract smoothly [INDEX].
    """
    # Dynamic fixture lookup path resolution [INDEX]
    event_row_mock = request.getfixturevalue(event_fixture_name)
    
    # We turn the dictionary into an object to match the SQLAlchemy row-mapping interfaces [INDEX]
    class StructEventRow:
        def __init__(self, d):
            self.event_id = d["event_id"]
            self.event_type = d["event_type"]
            self.event_version = d["event_version"]
            self.run_id = d["run_id"]
            self.payload = d["payload"]

    mock_row = StructEventRow(event_row_mock)
    mock_conn = MockDbConnection()
    
    try:
        # Route through your active version-aware registry engine
        handle_quality_failure_event(mock_conn, mock_row)
    except Exception as exc:
        pytest.fail(f"Consumer logic crashed processing supported historical variant '{event_fixture_name}': {exc}")
def test_forced_intentional_contract_breach_for_ci_verification(quality_failure_v1_contract_mock):
    """Deliberately corrupts the contract payload format to ensure the testing layer catches the error [INDEX]."""
    # Force an invalid data type into an integer-constrained column [INDEX]
    quality_failure_v1_contract_mock["payload"]["failed_records"] = "CRITICAL_ERROR"
    result = validate_event(quality_failure_v1_contract_mock)
    # This assertion will fail because an invalid type should make result['valid'] False [INDEX]
    assert result["valid"] is True 
