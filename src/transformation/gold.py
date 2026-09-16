
import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def get_affected_site_dates_from_silver(last_measurement_id):
    """
    Identifies site/date partitions affected by new Silver measurements.

    Gold grain:
        one row per site per calendar day
    """
    logger.info(
        f"Scanning for modified site/date partitions above "
        f"silver measurement_id={last_measurement_id}"
    )

    query = text("""
        SELECT DISTINCT
            site_id,
            DATE(measured_at) AS measurement_date
        FROM silver_measurements
        WHERE measurement_id > :last_measurement_id
        ORDER BY site_id, measurement_date;
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {"last_measurement_id": last_measurement_id},
        ).mappings().all()

    logger.info(
        f"Analysis complete. Affected staging grains located: {len(rows)}"
    )
    return rows


def refresh_gold_from_silver_incremental(last_measurement_id):
    """
    Incrementally recalculates Gold site/day aggregates for partitions
    affected by new Silver measurements.

    Gold grain:
        one row per site per calendar day
    """
    logger.info(
        f"Executing incremental Gold aggregate sweep above "
        f"silver measurement_id={last_measurement_id}"
    )

    query = text("""
        INSERT INTO gold_site_daily_performance (
            site_id,
            site_name,
            region,
            district,
            measurement_date,
            measurement_count,
            avg_traffic_mb,
            avg_latency_ms,
            avg_packet_loss_pct,
            avg_signal_strength_dbm,
            avg_availability_pct
        )
        SELECT
            s.site_id,
            s.site_name,
            s.region,
            s.district,
            DATE(sm.measured_at) AS measurement_date,
            COUNT(*) AS measurement_count,
            ROUND(AVG(sm.traffic_mb)::numeric, 2),
            ROUND(AVG(sm.latency_ms)::numeric, 2),
            ROUND(AVG(sm.packet_loss_pct)::numeric, 2),
            ROUND(AVG(sm.signal_strength_dbm)::numeric, 2),
            ROUND(AVG(sm.availability_pct)::numeric, 2)
        FROM silver_measurements sm
        JOIN sites s
            ON s.site_id = sm.site_id
        WHERE (sm.site_id, DATE(sm.measured_at)) IN (
            SELECT DISTINCT
                site_id,
                DATE(measured_at)
            FROM silver_measurements
            WHERE measurement_id > :last_measurement_id
        )
        GROUP BY
            s.site_id,
            s.site_name,
            s.region,
            s.district,
            DATE(sm.measured_at)
        ON CONFLICT (site_id, measurement_date)
        DO UPDATE SET
            site_name = EXCLUDED.site_name,
            region = EXCLUDED.region,
            district = EXCLUDED.district,
            measurement_count = EXCLUDED.measurement_count,
            avg_traffic_mb = EXCLUDED.avg_traffic_mb,
            avg_latency_ms = EXCLUDED.avg_latency_ms,
            avg_packet_loss_pct = EXCLUDED.avg_packet_loss_pct,
            avg_signal_strength_dbm = EXCLUDED.avg_signal_strength_dbm,
            avg_availability_pct = EXCLUDED.avg_availability_pct;
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {"last_measurement_id": last_measurement_id},
        )
        row_count = result.rowcount

    logger.info(
        f"Incremental Gold upsert execution complete. "
        f"Modified records: {row_count}"
    )
    return row_count


def refresh_gold_site_daily_incremental(min_raw_measurement_id):
    """
    Fallback RAW ID-based incremental driver preserved for
    historical test compatibility.

    Gold grain:
        one row per site per calendar day
    """
    query = text("""
        INSERT INTO gold_site_daily_performance (
            site_id,
            site_name,
            region,
            district,
            measurement_date,
            measurement_count,
            avg_traffic_mb,
            avg_latency_ms,
            avg_packet_loss_pct,
            avg_signal_strength_dbm,
            avg_availability_pct
        )
        SELECT
            s.site_id,
            s.site_name,
            s.region,
            s.district,
            DATE(sm.measured_at),
            COUNT(*),
            ROUND(AVG(sm.traffic_mb)::numeric, 2),
            ROUND(AVG(sm.latency_ms)::numeric, 2),
            ROUND(AVG(sm.packet_loss_pct)::numeric, 2),
            ROUND(AVG(sm.signal_strength_dbm)::numeric, 2),
            ROUND(AVG(sm.availability_pct)::numeric, 2)
        FROM silver_measurements sm
        JOIN sites s
            ON s.site_id = sm.site_id
        WHERE (sm.site_id, DATE(sm.measured_at)) IN (
            SELECT DISTINCT
                site_id,
                DATE(measured_at)
            FROM silver_measurements
            WHERE measurement_id IN (
                SELECT r.measurement_id
                FROM raw_measurements r
                WHERE r.raw_measurement_id > :min_raw_measurement_id
            )
        )
        GROUP BY
            s.site_id,
            s.site_name,
            s.region,
            s.district,
            DATE(sm.measured_at)
        ON CONFLICT (site_id, measurement_date)
        DO UPDATE SET
            site_name = EXCLUDED.site_name,
            region = EXCLUDED.region,
            district = EXCLUDED.district,
            measurement_count = EXCLUDED.measurement_count,
            avg_traffic_mb = EXCLUDED.avg_traffic_mb,
            avg_latency_ms = EXCLUDED.avg_latency_ms,
            avg_packet_loss_pct = EXCLUDED.avg_packet_loss_pct,
            avg_signal_strength_dbm = EXCLUDED.avg_signal_strength_dbm,
            avg_availability_pct = EXCLUDED.avg_availability_pct;
    """)

    with engine.begin() as connection:
        return connection.execute(
            query,
            {"min_raw_measurement_id": min_raw_measurement_id},
        ).rowcount


def run_gold():
    """Legacy full-load fallback method for backwards compatibility."""

    query = text("""
        INSERT INTO gold_site_daily_performance (
            site_id,
            site_name,
            region,
            district,
            measurement_date,
            measurement_count
        )
        SELECT
            s.site_id,
            s.site_name,
            s.region,
            s.district,
            DATE(sm.measured_at),
            COUNT(*)
        FROM silver_measurements sm
        JOIN sites s
            ON s.site_id = sm.site_id
        GROUP BY
            s.site_id,
            s.site_name,
            s.region,
            s.district,
            DATE(sm.measured_at)
        ON CONFLICT (site_id, measurement_date)
        DO UPDATE SET
            measurement_count = EXCLUDED.measurement_count;
    """)

    with engine.begin() as connection:
        return connection.execute(query).rowcount
