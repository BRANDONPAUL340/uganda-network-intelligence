import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def load_gold_site_daily_performance(run_id):
    """Computes daily geographical site aggregations and returns written row counts."""
    sql = """
    INSERT INTO gold_site_daily_performance (
        site_id, site_name, measurement_date, measurement_count, avg_traffic_mb,
        avg_latency_ms, avg_packet_loss_pct, avg_signal_strength_dbm, avg_availability_pct
    )
    SELECT 
        site_id, 
        MAX(site_name), 
        measured_at::DATE, 
        COUNT(*), 
        AVG(traffic_mb),
        AVG(latency_ms), 
        AVG(packet_loss_pct), 
        AVG(signal_strength_dbm), 
        AVG(availability_pct)
    FROM silver_measurements
    GROUP BY site_id, measured_at::DATE
    ON CONFLICT (site_id, measurement_date) DO UPDATE SET
        measurement_count = EXCLUDED.measurement_count,
        avg_traffic_mb = EXCLUDED.avg_traffic_mb,
        avg_latency_ms = EXCLUDED.avg_latency_ms,
        avg_packet_loss_pct = EXCLUDED.avg_packet_loss_pct,
        avg_signal_strength_dbm = EXCLUDED.avg_signal_strength_dbm,
        avg_availability_pct = EXCLUDED.avg_availability_pct;
    """
    with engine.begin() as connection:
        result = connection.execute(text(sql))
        return result.rowcount


def load_gold_equipment_health(run_id):
    """
    Computes downstream hardware asset ranking metrics and returns written row counts.
    Groups strictly by equipment_id to safely avoid CardinalityViolation exceptions.
    """
    sql = """
    INSERT INTO gold_equipment_health (
        equipment_id, equipment_type, manufacturer, model, measurement_count,
        avg_latency_ms, avg_packet_loss_pct, avg_availability_pct, health_status
    )
    SELECT 
        equipment_id, 
        MAX(equipment_type), 
        MAX(manufacturer), 
        MAX(model), 
        COUNT(*),
        AVG(latency_ms), 
        AVG(packet_loss_pct), 
        AVG(availability_pct),
        CASE 
            WHEN AVG(availability_pct) < 95 THEN 'Critical'
            WHEN AVG(availability_pct) < 98 THEN 'Warning'
            ELSE 'Healthy'
        END
    FROM silver_network_health
    GROUP BY equipment_id
    ON CONFLICT (equipment_id) DO UPDATE SET
        measurement_count = EXCLUDED.measurement_count,
        avg_latency_ms = EXCLUDED.avg_latency_ms,
        avg_packet_loss_pct = EXCLUDED.avg_packet_loss_pct,
        avg_availability_pct = EXCLUDED.avg_availability_pct,
        health_status = EXCLUDED.health_status;
    """
    with engine.begin() as connection:
        result = connection.execute(text(sql))
        return result.rowcount


def run_gold(run_id=112):
    """
    Orchestrates the entire Gold layer analytical summary sweep.
    Returns a dictionary map of newly processed row counts per target table.
    """
    print("\n--- GOLD LAYER ---")
    logger.info(f"Initializing Gold analytical layer calculation loop for run_id={run_id}")
    
    print("Refreshing gold_site_daily_performance aggregates...")
    site_count = load_gold_site_daily_performance(run_id)
    
    print("Refreshing gold_equipment_health aggregates...")
    equipment_count = load_gold_equipment_health(run_id)
    
    print(f"Gold site performance aggregations refreshed: {site_count}")
    print(f"Gold equipment health metrics scorecards refreshed: {equipment_count}")
    
    logger.info(f"Gold layer processing complete | site_records={site_count} | equipment_records={equipment_count}")
    
    return {
        "gold_site_daily_performance": site_count,
        "gold_equipment_health": equipment_count
    }
