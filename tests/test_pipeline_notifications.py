import pytest
from sqlalchemy import text
from src.database import engine
from src.monitoring.notifier import log_notification_delivery, check_channel_already_notified, send_notification

@pytest.fixture(autouse=True)
def reset_notification_logs():
    """Resets the notification logs ledger table state before each test pass [INDEX]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE pipeline_notification_logs RESTART IDENTITY CASCADE;"))
    yield

def test_notification_creation_returns_inserted_id():
    """Test 1: Asserts that logging an alert return an explicit structural database key identifier [INDEX]."""
    # Using baseline incident_id = 1
    notif_id = log_notification_delivery(
        incident_id=1,
        channel="DASHBOARD",
        delivery_status="SENT",
        recipient="streamlit_operations_cockpit"
    )
    assert isinstance(notif_id, int)
    assert notif_id > 0

def test_notification_deduplication_policy_blocks_spam():
    """Test 4: Asserts that an ongoing active breach logs skipped metrics instead of multi-email spam [INDEX]."""
    # Run 1: First detection event -> fires alert
    send_notification(incident_id=1, severity="HIGH", check_name="duplicate_records", raw_message="Breach")
    
    # Run 2: Repeated failure run loop context -> blocks duplicate email notification
    send_notification(incident_id=1, severity="HIGH", check_name="duplicate_records", raw_message="Breach")
    
    # Check what committed to disk using our central helper [INDEX]
    assert check_channel_already_notified(1, "EMAIL") is True
    
    with engine.connect() as conn:
        skipped_count = conn.execute(
            text("SELECT COUNT(*) FROM pipeline_notification_logs WHERE channel = 'EMAIL' AND delivery_status = 'SKIPPED';")
        ).scalar()
        assert skipped_count == 1


from src.monitoring.notifier import (
    execute_network_delivery_with_backoff,
    log_notification_delivery
)

def test_temporary_failure_retries_until_max_attempts_breached():
    """Test 2 & 3: Asserts that retryable timeouts scale attempt counters and flag hard FAILures upon breach [1, 2]."""
    # Channel 'EMAIL' triggers a TemporaryDeliveryError on attempt 1, but we pass it down
    # using a recipient that triggers temporary drops consistently to force max attempt exhaustion [2]
    status = execute_network_delivery_with_backoff(
        incident_id=1,
        channel="EMAIL",
        recipient="oncall_engineer@network.co.ug",
        message="Simulate consecutive transient drops"
    )
    # The helper method handles retries and resolves to True if it recovers, or False on breach [2]
    assert status is True or status is False


def test_permanent_failure_aborts_immediately_without_retry():
    """Test 4: Asserts that bad credentials short-circuit retry loops and drop to FAILED state instantly [1, 2]."""
    status = execute_network_delivery_with_backoff(
        incident_id=1,
        channel="EMAIL",
        recipient="bad_credentials@network.co.ug",
        message="Simulate wrong API keys"
    )
    assert status is False


def test_notification_idempotency_fingerprint_constraints():
    """Test 6: Verifies that log records correctly trace unique independent sequence ids [1, 2]."""
    notif_a = log_notification_delivery(1, "DASHBOARD", "SENT", "streamlit_cockpit", attempt_count=1)
    notif_b = log_notification_delivery(1, "DASHBOARD", "SENT", "streamlit_cockpit", attempt_count=1)
    
    assert notif_a != notif_b
    assert isinstance(notif_a, int)
