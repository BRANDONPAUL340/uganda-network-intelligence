from sqlalchemy import text

from src.database import engine
from src.logger import get_logger

# Initialize our module-level logger instance
logger = get_logger(__name__)


def get_latest_successful_batch():
    """
    Returns the latest successful batch_id from the metadata registry.
    """
    sql = """
    SELECT batch_id
    FROM source_batches
    WHERE status = 'SUCCESS'
    ORDER BY batch_id DESC
    LIMIT 1;
    """
    with engine.begin() as connection:
        result = connection.execute(text(sql))
        return result.scalar()


def get_affected_site_dates(batch_id):
    """
    Extracts ONLY the site and date slices modified within the specific batch.
    """
    sql = """
    SELECT DISTINCT
        site_id,
        measured_at::date AS measurement_date
    FROM silver_measurements
    WHERE batch_id = :batch_id
    ORDER BY
        measurement_date,
        site_id;
    """
    with engine.begin() as connection:
        result = connection.execute(text(sql), {"batch_id": batch_id})
        return result.fetchall()


def calculate_site_daily_performance(site_id, measurement_date):
    """
    Extracts aggregated statistics for a specific site/date partition.
    """
    sql = """
    SELECT
        site_id,
        MAX(site_name) AS site_name,
        MAX(region) AS region,
        MAX(district) AS district,
        measured_at::date AS measurement_date,
        COUNT(*) AS measurement_count,
        ROUND(AVG(traffic_mb), 2) AS avg_traffic_mb,
        ROUND(AVG(latency_ms), 2) AS avg_latency_ms,
        ROUND(AVG(packet_loss_pct), 2) AS avg_packet_loss_pct,
        ROUND(AVG(signal_strength_dbm), 2) AS avg_signal_strength_dbm,
        ROUND(AVG(availability_pct), 2) AS avg_availability_pct
    FROM silver_measurements
    WHERE site_id = :site_id AND measured_at::date = :measurement_date
    GROUP BY site_id, measured_at::date;
    """
    with engine.begin() as connection:
        result = connection.execute(
            text(sql),
            {
                "site_id": site_id,
                "measurement_date": measurement_date
            }
        )
        return result.fetchone()


def upsert_site_daily_performance(row):
    """
    Executes a high-performance database upsert statement to update Gold summary tables.
    """
    if row is None:
        return

    sql = """
    INSERT INTO gold_site_daily_performance (
        site_id, site_name, region, district, measurement_date,
        measurement_count, avg_traffic_mb, avg_latency_ms,
        avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct,
        updated_at
    )
    VALUES (
        :site_id, :site_name, :region, :district, :measurement_date,
        :measurement_count, :avg_traffic_mb, :avg_latency_ms,
        :avg_packet_loss_pct, :avg_signal_strength_dbm, :avg_availability_pct,
        CURRENT_TIMESTAMP
    )
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
        avg_availability_pct = EXCLUDED.avg_availability_pct,
        updated_at = CURRENT_TIMESTAMP;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "site_id": row.site_id,
                "site_name": row.site_name,
                "region": row.region,
                "district": row.district,
                "measurement_date": row.measurement_date,
                "measurement_count": row.measurement_count,
                "avg_traffic_mb": row.avg_traffic_mb,
                "avg_latency_ms": row.avg_latency_ms,
                "avg_packet_loss_pct": row.avg_packet_loss_pct,
                "avg_signal_strength_dbm": row.avg_signal_strength_dbm,
                "avg_availability_pct": row.avg_availability_pct,
            }
        )


def create_gold_equipment_health():
    """
    Refreshes equipment hardware health summaries.
    """
    logger.info("Refreshing gold_equipment_health metrics matrix...")
    sql = """
    CREATE TABLE IF NOT EXISTS gold_equipment_health AS
    SELECT
        equipment_id, equipment_type, manufacturer, model, COUNT(*) AS measurement_count,
        ROUND(AVG(latency_ms), 2) AS avg_latency_ms,
        ROUND(AVG(packet_loss_pct), 2) AS avg_packet_loss_pct,
        ROUND(AVG(signal_strength_dbm), 2) AS avg_signal_strength_dbm,
        ROUND(AVG(availability_pct), 2) AS avg_availability_pct,
        CASE
            WHEN AVG(availability_pct) < 95 OR AVG(packet_loss_pct) > 5 OR AVG(latency_ms) > 70 THEN 'Critical'
            WHEN AVG(availability_pct) < 98 OR AVG(packet_loss_pct) > 2 OR AVG(latency_ms) > 40 THEN 'Warning'
            ELSE 'Healthy'
        END AS health_status
    FROM silver_measurements
    GROUP BY equipment_id, equipment_type, manufacturer, model;
    """
    refresh_sql = """
    TRUNCATE TABLE gold_equipment_health;
    INSERT INTO gold_equipment_health
    SELECT
        equipment_id, equipment_type, manufacturer, model, COUNT(*),
        ROUND(AVG(latency_ms), 2), ROUND(AVG(packet_loss_pct), 2),
        ROUND(AVG(signal_strength_dbm), 2), ROUND(AVG(availability_pct), 2),
        CASE
            WHEN AVG(availability_pct) < 95 OR AVG(packet_loss_pct) > 5 OR AVG(latency_ms) > 70 THEN 'Critical'
            WHEN AVG(availability_pct) < 98 OR AVG(packet_loss_pct) > 2 OR AVG(latency_ms) > 40 THEN 'Warning'
            ELSE 'Healthy'
        END
    FROM silver_measurements
    GROUP BY equipment_id, equipment_type, manufacturer, model;
    """
    with engine.begin() as connection:
        connection.execute(text(sql))
        connection.execute(text(refresh_sql))
    logger.info("gold_equipment_health tracking matrix successfully updated.")


def run_incremental_gold():
    """
    Orchestrates the high-performance incremental aggregation runner loop.
    """
    logger.info("--- INCREMENTAL GOLD LAYER ---")

    batch_id = get_latest_successful_batch()

    if batch_id is None:
        logger.info("No successful ingestion batch found.")
        return 0

    logger.info(f"Processing batch: {batch_id}")

    affected = get_affected_site_dates(batch_id)

    processed = 0

    for site_id, measurement_date in affected:
        logger.info(f"Computing incremental summary for Site ID {site_id} on Date {measurement_date}")
        row = calculate_site_daily_performance(site_id, measurement_date)

        if row:
            upsert_site_daily_performance(row)
            processed += 1

    logger.info(f"Gold combinations processed: {processed}")
    return processed


def run_gold():
    """
    Unified entry point matching our master workflow wrapper criteria.
    """
    logger.info("--- GOLD LAYER ---")
    
    processed = run_incremental_gold()
    
    # Maintain equipment matrices configurations
    create_gold_equipment_health()

    return {
        "gold_records_processed": processed
    }


if __name__ == "__main__":
    run_gold()
