from sqlalchemy import text

from src.database import engine


def create_gold_site_daily_performance():

    print("Refreshing gold_site_daily_performance...")

    sql = """
    CREATE TABLE IF NOT EXISTS gold_site_daily_performance AS

    SELECT
        site_id,
        site_name,
        region,
        district,
        DATE(measured_at) AS measurement_date,

        COUNT(*) AS measurement_count,

        ROUND(AVG(traffic_mb), 2)
            AS avg_traffic_mb,

        ROUND(AVG(latency_ms), 2)
            AS avg_latency_ms,

        ROUND(AVG(packet_loss_pct), 2)
            AS avg_packet_loss_pct,

        ROUND(AVG(signal_strength_dbm), 2)
            AS avg_signal_strength_dbm,

        ROUND(AVG(availability_pct), 2)
            AS avg_availability_pct

    FROM silver_measurements

    GROUP BY
        site_id,
        site_name,
        region,
        district,
        DATE(measured_at);
    """

    refresh_sql = """
    TRUNCATE TABLE gold_site_daily_performance;

    INSERT INTO gold_site_daily_performance

    SELECT
        site_id,
        site_name,
        region,
        district,
        DATE(measured_at) AS measurement_date,

        COUNT(*) AS measurement_count,

        ROUND(AVG(traffic_mb), 2),
        ROUND(AVG(latency_ms), 2),
        ROUND(AVG(packet_loss_pct), 2),
        ROUND(AVG(signal_strength_dbm), 2),
        ROUND(AVG(availability_pct), 2)

    FROM silver_measurements

    GROUP BY
        site_id,
        site_name,
        region,
        district,
        DATE(measured_at);
    """

    with engine.begin() as connection:

        connection.execute(text(sql))

        connection.execute(
            text(refresh_sql)
        )

    print("gold_site_daily_performance refreshed.")


def create_gold_equipment_health():

    print("Refreshing gold_equipment_health...")

    sql = """
    CREATE TABLE IF NOT EXISTS gold_equipment_health AS

    SELECT
        equipment_id,
        equipment_type,
        manufacturer,
        model,

        COUNT(*) AS measurement_count,

        ROUND(AVG(latency_ms), 2)
            AS avg_latency_ms,

        ROUND(AVG(packet_loss_pct), 2)
            AS avg_packet_loss_pct,

        ROUND(AVG(signal_strength_dbm), 2)
            AS avg_signal_strength_dbm,

        ROUND(AVG(availability_pct), 2)
            AS avg_availability_pct,

        CASE
            WHEN
                AVG(availability_pct) < 95
                OR AVG(packet_loss_pct) > 5
                OR AVG(latency_ms) > 70
            THEN 'Critical'

            WHEN
                AVG(availability_pct) < 98
                OR AVG(packet_loss_pct) > 2
                OR AVG(latency_ms) > 40
            THEN 'Warning'

            ELSE 'Healthy'
        END AS health_status

    FROM silver_measurements

    GROUP BY
        equipment_id,
        equipment_type,
        manufacturer,
        model;
    """

    # 🛠️ Fixed: Changed legacy_ms to AVG(latency_ms) to align properly!
    refresh_sql = """
    TRUNCATE TABLE gold_equipment_health;

    INSERT INTO gold_equipment_health

    SELECT
        equipment_id,
        equipment_type,
        manufacturer,
        model,

        COUNT(*),
        ROUND(AVG(latency_ms), 2),
        ROUND(AVG(packet_loss_pct), 2),
        ROUND(AVG(signal_strength_dbm), 2),
        ROUND(AVG(availability_pct), 2),

        CASE
            WHEN
                AVG(availability_pct) < 95
                OR AVG(packet_loss_pct) > 5
                OR AVG(latency_ms) > 70
            THEN 'Critical'

            WHEN
                AVG(availability_pct) < 98
                OR AVG(packet_loss_pct) > 2
                OR AVG(latency_ms) > 40
            THEN 'Warning'

            ELSE 'Healthy'
        END

    FROM silver_measurements

    GROUP BY
        equipment_id,
        equipment_type,
        manufacturer,
        model;
    """

    with engine.begin() as connection:

        connection.execute(text(sql))

        connection.execute(
            text(refresh_sql)
        )

    print("gold_equipment_health refreshed.")


def run_gold():

    print("\n--- GOLD LAYER ---")

    create_gold_site_daily_performance()

    create_gold_equipment_health()


if __name__ == "__main__":
    run_gold()
