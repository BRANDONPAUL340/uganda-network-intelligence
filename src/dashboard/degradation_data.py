
"""Read-only data access for the network degradation dashboard."""

import logging

import pandas as pd
from sqlalchemy import text

from src.database import engine
from src.monitoring.degradation import evaluate_all_sites

logger = logging.getLogger(__name__)

MEASUREMENTS_PER_SITE = 30

DEGRADATION_HISTORY_QUERY = text("""
    WITH ranked_measurements AS (
        SELECT
            measurement_id,
            measured_at,
            site_id,
            site_name,
            latency_ms,
            packet_loss_pct,
            availability_pct,
            signal_strength_dbm,
            ROW_NUMBER() OVER (
                PARTITION BY site_id
                ORDER BY measured_at DESC, measurement_id DESC
            ) AS row_number
        FROM silver_measurements
        WHERE site_id IS NOT NULL
          AND measured_at IS NOT NULL
    )
    SELECT
        measurement_id,
        measured_at,
        site_id,
        site_name,
        latency_ms,
        packet_loss_pct,
        availability_pct,
        signal_strength_dbm
    FROM ranked_measurements
    WHERE row_number <= :rows_per_site
    ORDER BY site_id, measured_at ASC, measurement_id ASC
""")


def load_degradation_assessments() -> dict:
    """Load recent site histories and evaluate them without database writes."""
    try:
        with engine.connect() as connection:
            measurements = pd.read_sql_query(
                DEGRADATION_HISTORY_QUERY,
                connection,
                params={"rows_per_site": MEASUREMENTS_PER_SITE},
            )

        if measurements.empty:
            return {
                "ok": True,
                "assessments": [],
                "measurement_count": 0,
                "error": None,
            }

        records = measurements.to_dict(orient="records")
        assessments = evaluate_all_sites(records)

        return {
            "ok": True,
            "assessments": assessments,
            "measurement_count": len(measurements),
            "error": None,
        }

    except Exception:
        logger.exception("Failed to load degradation assessment data")

        return {
            "ok": False,
            "assessments": [],
            "measurement_count": 0,
            "error": (
                "Could not load network measurement history. "
                "Check the database connection, permissions, and schema."
            ),
        }
