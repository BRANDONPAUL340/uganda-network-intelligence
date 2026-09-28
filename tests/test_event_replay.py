
import pytest
from sqlalchemy import text

from src.database import engine
from src.monitoring.event_store import (
    publish_quality_event,
    consume_event_store_stream,
    force_replay_specific_event,
    backfill_events_for_pipeline_run,
)


@pytest.fixture
def pipeline_run_id():
    """
    Create an isolated completed pipeline run for each test.
    """
    with engine.begin() as conn:
        run_id = conn.execute(
            text(
                """
                INSERT INTO pipeline_runs (
                    pipeline_name,
                    status
                )
                VALUES (
                    'event_replay_test',
                    'COMPLETED'
                )
                RETURNING run_id;
                """
            )
        ).scalar_one()

    return run_id


@pytest.fixture
def quality_event_result():
    """
    Standard quality-check result used by the event-store tests.
    """
    return {
        "check_name": "null_site_id",
        "status": "FAIL",
        "failed_records": 8,
        "message": "Null keys found.",
    }


def test_publish_quality_event_creates_event(
    pipeline_run_id,
    quality_event_result,
):
    """
    Verify that publish_quality_event successfully creates
    and returns a historical event identifier.
    """
    event_id = publish_quality_event(
        run_id=pipeline_run_id,
        result=quality_event_result,
    )

    assert event_id is not None


def test_consume_event_store_stream_returns_events(
    pipeline_run_id,
    quality_event_result,
):
    """
    Verify that the event-store consumer can read published events.
    """
    event_id = publish_quality_event(
        run_id=pipeline_run_id,
        result=quality_event_result,
    )

    assert event_id is not None

    events = consume_event_store_stream()

    assert events is not None


def test_force_replay_reprocesses_historical_event_successfully(
    pipeline_run_id,
    quality_event_result,
):
    """
    Verify that a historical event can be explicitly replayed.
    """
    event_id = publish_quality_event(
        run_id=pipeline_run_id,
        result=quality_event_result,
    )

    assert event_id is not None

    replay_result = force_replay_specific_event(event_id)

    assert replay_result is not None


def test_backfill_events_for_pipeline_run_completes_successfully(
    pipeline_run_id,
    quality_event_result,
):
    """
    Verify that historical events associated with a pipeline run
    can be backfilled successfully.
    """
    event_id = publish_quality_event(
        run_id=pipeline_run_id,
        result=quality_event_result,
    )

    assert event_id is not None

    backfill_result = backfill_events_for_pipeline_run(
        pipeline_run_id
    )

    assert backfill_result is not None