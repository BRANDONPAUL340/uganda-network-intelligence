import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def get_affected_site_dates(min_raw_measurement_id):
    """
    Diagnostic Selector: Identifies which specific site and date combinations 
    were affected by the latest raw data delta slice above the watermark pointer [INDEX].
    Uses 'measured_at' to match your production Silver table layout [INDEX].
    """
    logger.info(f"Scanning for affected site/date partitions above raw_id={min_raw_measurement_id}")
    
    query = text("""
        SELECT DISTINCT
            site_id,
            measured_at AS measurement_date
        FROM silver_measurements
        WHERE measurement_id IN (
            SELECT r.measurement_id
            FROM raw_measurements r
            WHERE r.raw_measurement_id > :min_raw_measurement_id
        )
        ORDER BY site_id, measured_at;
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "min_raw_measurement_id": min_raw_measurement_id,
            },
        ).mappings().all()

    logger.info(f"Analysis complete. Affected site/date grains located: {len(rows)}")
    return rows


def refresh_gold_site_daily_incremental(min_raw_measurement_id):
    """
    High-Performance Gold Incremental Updater: Recalculates aggregates ONLY for the 
    affected site/date slices using an idempotent merge upsert pattern [INDEX].
    Leaves historical analytics cubes completely untouched [INDEX].
    """
    affected = get_affected_site_dates(min_raw_measurement_id)

    if not affected:
        logger.info("No affected site/date grains detected. Skipping Gold update pass.")
        return 0

    logger.info(f"Executing incremental Gold upsert block for {len(affected)} target dimensions...")

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
            sm.measured_at AS measurement_date,
            COUNT(*) AS measurement_count,
            ROUND(AVG(sm.traffic_mb)::numeric, 2),
            ROUND(AVG(sm.latency_ms)::numeric, 2),
            ROUND(AVG(sm.packet_loss_pct)::numeric, 2),
            ROUND(AVG(sm.signal_strength_dbm)::numeric, 2),
            ROUND(AVG(sm.availability_pct)::numeric, 2)
        FROM silver_measurements sm
        JOIN sites s ON s.site_id = sm.site_id
        WHERE (sm.site_id, sm.measured_at) IN (
            SELECT DISTINCT
                site_id,
                measured_at
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
            sm.measured_at
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
            {
                "min_raw_measurement_id": min_raw_measurement_id,
            },
        )
        row_count = result.rowcount

    logger.info(f"Incremental Gold upsert execution complete. Modified records: {row_count}")
    return row_count


def run_gold():
    """Legacy full-load fallback method for backwards-compatibility checks."""
    logger.info("Running baseline legacy full Gold aggregate rebuild sweep...")
    query = text("""
        INSERT INTO gold_site_daily_performance (
            site_id, site_name, region, district, measurement_date,
            measurement_count, avg_traffic_mb, avg_latency_ms, avg_packet_loss_pct,
            avg_signal_strength_dbm, avg_availability_pct
        )
        SELECT
            s.site_id, s.site_name, s.region, s.district, sm.measured_at,
            COUNT(*), ROUND(AVG(sm.traffic_mb)::numeric, 2), ROUND(AVG(sm.latency_ms)::numeric, 2),
            ROUND(AVG(sm.packet_loss_pct)::numeric, 2), ROUND(AVG(sm.signal_strength_dbm)::numeric, 2),
            ROUND(AVG(sm.availability_pct)::numeric, 2)
        FROM silver_measurements sm
        JOIN sites s ON s.site_id = sm.site_id
        GROUP BY s.site_id, s.site_name, s.region, s.district, sm.measured_at
        ON CONFLICT (site_id, measurement_date) DO UPDATE SET
            measurement_count = EXCLUDED.measurement_count,
            avg_traffic_mb = EXCLUDED.avg_traffic_mb;
    """)
    with engine.begin() as connection:
        result = connection.execute(query)
        return result.rowcount
