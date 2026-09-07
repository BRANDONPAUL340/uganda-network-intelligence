from sqlalchemy import text
from src.database import engine
from src.logger import get_logger

# Initialize package-level logger instance
logger = get_logger(__name__)


def create_gold_site_daily_performance():
    """
    Computes and updates daily analytical summaries at the site layer.
    """
    logger.info("Refreshing gold_site_daily_performance aggregates...")
    
    # 🔑 Fixed: Target the correct physical name "gold_site_daily_performance"
    refresh_sql = """
    TRUNCATE TABLE gold_site_daily_performance CASCADE;
    INSERT INTO gold_site_daily_performance (
        site_id, site_name, district, measurement_count,
        avg_traffic_mb, avg_latency_ms, avg_packet_loss_pct, avg_availability_pct, updated_at
    )
    SELECT 
        site_id, site_name, max(district), COUNT(*),
        ROUND(AVG(traffic_mb), 2), ROUND(AVG(latency_ms), 2),
        ROUND(AVG(packet_loss_pct), 2), ROUND(AVG(availability_pct), 2),
        CURRENT_TIMESTAMP
    FROM silver_network_health
    GROUP BY site_id, site_name;
    """
    with engine.begin() as connection:
        connection.execute(text(refresh_sql))
        
        count_sql = "SELECT COUNT(*) FROM gold_site_daily_performance;"
        return connection.execute(text(count_sql)).scalar()


def create_gold_equipment_health():
    """
    Computes and updates health metrics scorecards at the hardware equipment layer.
    Using ON CONFLICT handles structural duplicates safely.
    """
    logger.info("Refreshing gold_equipment_health aggregates...")
    
    refresh_sql = """
    TRUNCATE TABLE gold_equipment_health CASCADE;
    INSERT INTO gold_equipment_health (
        equipment_id, equipment_type, manufacturer, model, measurement_count,
        avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct,
        health_status, record_count, updated_at
    )
    SELECT 
        equipment_id, max(equipment_type), max(manufacturer), max(model), COUNT(*),
        ROUND(AVG(latency_ms), 2), ROUND(AVG(packet_loss_pct), 2),
        ROUND(AVG(signal_strength_dbm), 2), ROUND(AVG(availability_pct), 2),
        CASE 
            WHEN AVG(availability_pct) < 95 OR AVG(packet_loss_pct) > 5 OR AVG(latency_ms) > 70 THEN 'Critical'
            WHEN AVG(availability_pct) < 98 OR AVG(packet_loss_pct) > 2 OR AVG(latency_ms) > 40 THEN 'Warning'
            ELSE 'Healthy'
        END,
        COUNT(*), CURRENT_TIMESTAMP
    FROM silver_measurements
    GROUP BY equipment_id;
    """
    with engine.begin() as connection:
        connection.execute(text(refresh_sql))
        
        count_sql = "SELECT COUNT(*) FROM gold_equipment_health;"
        return connection.execute(text(count_sql)).scalar()


def run_gold(run_id=None):
    """
    Orchestrates the materialisation of analytical reporting targets inside the Gold layer.
    """
    print("\n--- GOLD LAYER ---")
    logger.info(f"Initializing Gold analytical layer calculation loop for run_id={run_id}")

    site_count = create_gold_site_daily_performance()
    equipment_count = create_gold_equipment_health()

    print(f"Gold site performance aggregations refreshed: {site_count}")
    print(f"Gold equipment health metrics scorecards refreshed: {equipment_count}")
    
    logger.info(f"Gold layer processing complete | site_records={site_count} | equipment_records={equipment_count}")
    
    return {
        "site_daily_performance": site_count,
        "equipment_health": equipment_count
    }
