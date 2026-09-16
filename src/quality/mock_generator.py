import datetime
import random
import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)

def generate_bulk_raw_telemetry(record_count=100000):
    """
    Generates and bulk-inserts high-volume synthetic telemetry rows into raw_measurements
    to test query planner optimization thresholds under realistic enterprise data scales [INDEX].
    """
    logger.info(f"Initializing synthetic generation engine for {record_count} telemetry records...")
    
    # 1. Fetch valid site and equipment boundaries from active lookup catalogs
    with engine.connect() as conn:
        site_ids = [row[0] for row in conn.execute(text("SELECT site_id FROM sites;")).fetchall()]
        equip_ids = [row[0] for row in conn.execute(text("SELECT equipment_id FROM equipment;")).fetchall()]
    
    if not site_ids or not equip_ids:
        raise ValueError("Cannot run generator: Ensure master 'sites' and 'equipment' tables have baseline records.")

    # 2. Structure bulk rows using fast batched parameter array mapping
    base_date = datetime.date(2026, 9, 14)
    query = text("""
        INSERT INTO raw_measurements (
            measurement_id, site_id, equipment_id, measurement_date,
            traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct, source_file
        ) VALUES (
            :measurement_id, :site_id, :equipment_id, :measurement_date,
            :traffic_mb, :latency_ms, :packet_loss_pct, :signal_strength_dbm, :availability_pct, :source_file
        );
    """)

    logger.info("Streaming parameters into memory buffers...")
    batch_size = 10000
    current_records = []
    
    # Start sequence range safely above standard testing identifiers
    start_id = 200001 

    with engine.begin() as transaction:
        for i in range(record_count):
            msg_id = start_id + i
            # Mix target dates across our benchmark testing points
            target_date = base_date - datetime.timedelta(days=random.randint(0, 5))
            
            row_data = {
                "measurement_id": msg_id,
                "site_id": random.choice(site_ids),
                "equipment_id": random.choice(equip_ids),
                "measurement_date": target_date,
                "traffic_mb": round(random.uniform(500.0, 50000.0), 2),
                "latency_ms": round(random.uniform(5.0, 150.0), 2),
                "packet_loss_pct": round(random.uniform(0.0, 5.0), 2),
                "signal_strength_dbm": random.randint(-90, -45),
                "availability_pct": round(random.uniform(95.0, 100.0), 2),
                "source_file": "bulk_scale_simulation.csv"
            }
            current_records.append(row_data)

            # Trigger transactional chunk flash writes to protect container RAM pools
            if len(current_records) >= batch_size:
                transaction.execute(query, current_records)
                current_records = []
                logger.info(f"Buffered write chunk committed: {i + 1}/{record_count} rows loaded.")
        
        if current_records:
            transaction.execute(query, current_records)

    logger.info(f"Successfully loaded {record_count} high-volume rows into the data lake.")
    return record_count
