from sqlalchemy import text

from src.database import engine


def create_silver_measurements():

    print("Creating silver_measurements...")

    sql = """
    DROP TABLE IF EXISTS silver_measurements CASCADE;

    CREATE TABLE silver_measurements AS
    SELECT
        m.measurement_id,
        m.measured_at,

        s.site_id,
        s.site_name,
        s.region,
        s.district,
        s.site_type,

        e.equipment_id,
        e.equipment_type,
        e.manufacturer,
        e.model,

        m.traffic_mb,
        m.latency_ms,
        m.packet_loss_pct,
        m.signal_strength_dbm,
        m.availability_pct

    FROM measurements m

    JOIN sites s
        ON m.site_id = s.site_id

    JOIN equipment e
        ON m.equipment_id = e.equipment_id;
    """

    with engine.begin() as connection:
        connection.execute(text(sql))

    print("silver_measurements created successfully.")


def create_silver_network_health():

    print("Creating silver_network_health...")

    sql = """
    DROP TABLE IF EXISTS silver_network_health CASCADE;

    CREATE TABLE silver_network_health AS
    SELECT
        measurement_id,
        measured_at,
        site_id,
        site_name,
        region,
        district,
        site_type,
        equipment_id,
        equipment_type,
        manufacturer,
        model,
        traffic_mb,
        latency_ms,
        packet_loss_pct,
        signal_strength_dbm,
        availability_pct,

        CASE
            WHEN
                availability_pct < 95
                OR packet_loss_pct > 5
                OR latency_ms > 70
            THEN 'Critical'

            WHEN
                availability_pct < 98
                OR packet_loss_pct > 2
                OR latency_ms > 40
            THEN 'Warning'

            ELSE 'Healthy'
        END AS health_status

    FROM silver_measurements;
    """

    with engine.begin() as connection:
        connection.execute(text(sql))

    print("silver_network_health created successfully.")


def run_silver():

    create_silver_measurements()
    create_silver_network_health()


if __name__ == "__main__":
    run_silver()
