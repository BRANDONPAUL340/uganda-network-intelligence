import pytest
from sqlalchemy import text
from src.database import engine
from src.monitoring.alerts import Alert
from src.monitoring.alert_store import save_alert, get_open_alert


@pytest.fixture(autouse=True)
def clean_alert_ledger():
    """Fixture to reset table status records before each pass [INDEX]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE alert_history RESTART IDENTITY CASCADE;"))
    yield


def test_backward_compatibility_uncorrelated_alert():
    """Asserts that legacy, uncorrelated alerts work perfectly, defaulting metadata to NULL [INDEX]."""
    alert = Alert(
        name="freshness_stale",
        severity="SEV3",
        message="Data is stale",
    )
    res = save_alert(alert)
    assert res["created"] is True

    open_alert = get_open_alert("freshness_stale")
    assert open_alert is not None
    assert open_alert["run_id"] is None
    assert open_alert["stage_name"] is None


def test_correlated_alert_saves_context_metadata():
    """Asserts that new, correlated alerts accurately preserve execution run and stage attributes [INDEX]."""
    alert = Alert(
        name="pipeline_failure",
        severity="SEV2",
        message="Pipeline failed",
        run_id=17,
        stage_name="SILVER",
    )
    res = save_alert(alert)
    assert res["created"] is True

    open_alert = get_open_alert("pipeline_failure")
    assert open_alert is not None
    assert open_alert["run_id"] == 17
    assert open_alert["stage_name"] == "SILVER"
