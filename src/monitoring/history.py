from sqlalchemy import text
from src.config import PIPELINE_NAME
from src.database import engine


def save_health_snapshot(report, alerts):
    """
    Durable Snapshot Writer: Extracted parameters are transformed into integer counts
    and transactionally logged onto disk to keep track of system metrics over time [INDEX].
    """
    checks = report["checks"]
    alert_count = len(alerts)

    critical_alert_count = sum(
        1 for alert in alerts if alert["severity"] == "CRITICAL"
    )
    warning_alert_count = sum(
        1 for alert in alerts if alert["severity"] == "WARNING"
    )

    query = text("""
        INSERT INTO pipeline_health_history (
            pipeline_name,
            overall_status,
            database_status,
            pipeline_run_status,
            pipeline_stage_status,
            alert_count,
            critical_alert_count,
            warning_alert_count
        )
        VALUES (
            :pipeline_name,
            :overall_status,
            :database_status,
            :pipeline_run_status,
            :pipeline_stage_status,
            :alert_count,
            :critical_alert_count,
            :warning_alert_count
        )
        RETURNING health_id;
    """)

    with engine.begin() as connection:
        health_id = connection.execute(
            query,
            {
                "pipeline_name": PIPELINE_NAME,
                "overall_status": report["overall_status"],
                "database_status": checks["database"],
                "pipeline_run_status": checks["latest_pipeline_run"],
                "pipeline_stage_status": checks["pipeline_stages"],
                "alert_count": alert_count,
                "critical_alert_count": critical_alert_count,
                "warning_alert_count": warning_alert_count,
            },
        ).scalar_one()

    return health_id
