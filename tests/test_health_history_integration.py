from sqlalchemy import text
from src.config import PIPELINE_NAME
from src.database import engine
from src.monitoring.history import save_health_snapshot


def test_health_snapshot_can_be_saved():
    """ARRANGE, ACT & ASSERT: Verifies end-to-end relational data snapshot persistence loops [INDEX]."""
    report = {
        "overall_status": "HEALTHY",
        "checks": {
            "database": "HEALTHY",
            "database_size": "HEALTHY",
            "dead_tuples": "HEALTHY",
            "latest_pipeline_run": "HEALTHY",
            "pipeline_stages": "HEALTHY",
        },
    }

    alerts = []

    # Persist snapshot entry
    health_id = save_health_snapshot(report, alerts)
    assert health_id is not None

    # Read back and assert structural consistency
    query = text("""
        SELECT pipeline_name, overall_status
        FROM pipeline_health_history
        WHERE health_id = :health_id;
    """)

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {"health_id": health_id},
        ).one()

    assert row[0] == PIPELINE_NAME
    assert row[1] == "HEALTHY"
