import pytest
from sqlalchemy import text
from src.database import engine
from src.monitoring.alerts import Alert
from src.monitoring.alert_store import save_alert, resolve_alert, get_open_alert


@pytest.fixture(autouse=True)
def clean_alert_history():
    """Fixture to ensure the alert_history table is completely clean before each test [INDEX]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE alert_history RESTART IDENTITY CASCADE;"))
    yield


def test_new_alert_creation_flow():
    """Test 1: Asserts that an alert is successfully generated when no matching OPEN incident exists [INDEX]."""
    alert = Alert(name="pipeline_failure", severity="SEV2", message="Ingestion pipeline failed")
    
    result = save_alert(alert)
    assert result["created"] is True
    assert result["alert_id"] is not None

    open_alert = get_open_alert("pipeline_failure")
    assert open_alert is not None
    assert open_alert["status"] == "OPEN"


def test_duplicate_alert_deduplication_fence():
    """Test 2: Asserts that duplicate rows are suppressed when a matching alert is already OPEN [INDEX]."""
    alert = Alert(name="pipeline_failure", severity="SEV2", message="Ingestion pipeline failed")
    
    # Fire the first alert to open the incident
    first_res = save_alert(alert)
    assert first_res["created"] is True

    # Fire the second alert to test the deduplication gate
    second_res = save_alert(alert)
    assert second_res["created"] is False
    assert second_res["alert_id"] == first_res["alert_id"]

    # Verify that the database contains exactly one row
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM alert_history;")).scalar()
        assert count == 1


def test_alert_resolution_transition():
    """Test 3: Asserts that an open incident transitions to RESOLVED with a timestamp [INDEX]."""
    alert = Alert(name="pipeline_sla_breach", severity="SEV3", message="SLA breach detected")
    save_alert(alert)

    # Resolve the active alert condition
    was_resolved = resolve_alert("pipeline_sla_breach")
    assert was_resolved is True

    # Verify state transitions inside database
    open_alert = get_open_alert("pipeline_sla_breach")
    assert open_alert is None  # Should be none because status is no longer OPEN

    with engine.connect() as conn:
        row = conn.execute(text("SELECT status, resolved_at FROM alert_history WHERE alert_name = 'pipeline_sla_breach';")).fetchone()
        assert row._mapping["status"] == "RESOLVED"
        assert row._mapping["resolved_at"] is not None


def test_new_alert_generation_after_resolution():
    """Test 4: Asserts that a new alert row is created if a failure occurs after a previous one was RESOLVED [INDEX]."""
    alert = Alert(name="freshness_stale", severity="SEV3", message="Data is lagging")
    
    # 1. First failure cycle
    res1 = save_alert(alert)
    resolve_alert("freshness_stale")

    # 2. Second failure cycle
    res2 = save_alert(alert)
    assert res2["created"] is True
    assert res2["alert_id"] != res1["alert_id"]

    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM alert_history;")).scalar()
        assert count == 2


def test_resolving_nonexistent_alert_grace():
    """Test 5: Asserts that attempting to resolve a nonexistent alert condition finishes gracefully without crashing [INDEX]."""
    was_resolved = resolve_alert("does_not_exist")
    assert was_resolved is False
