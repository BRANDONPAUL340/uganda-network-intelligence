from sqlalchemy import text

from src.database import engine


def create_gold_site_daily_performance():

    print("Creating gold_site_daily_performance...")

    sql = """
    DROP TABLE IF EXISTS gold_site_daily_performance;

    CREATE TABLE gold_site_daily_performance AS

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

    with engine.begin() as connection:
        connection.execute(text(sql))

    print("gold_site_daily_performance created.")


def create_gold_equipment_health():

    print("Creating gold_equipment_health...")

    sql = """
    DROP TABLE IF EXISTS gold_equipment_health;

    CREATE TABLE gold_equipment_health AS

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

    with engine.begin() as connection:
        connection.execute(text(sql))

    print("gold_equipment_health created.")


def create_gold_incident_summary():

    print("Creating gold_incident_summary...")

    sql = """
    DROP TABLE IF EXISTS gold_incident_summary;

    CREATE TABLE gold_incident_summary AS

    SELECT
        s.site_id,
        s.site_name,
        s.region,
        s.district,

        COUNT(i.incident_id) AS total_incidents,

        COUNT(*) FILTER (
            WHERE i.severity = 'Critical'
        ) AS critical_incidents,

        COUNT(*) FILTER (
            WHERE i.severity = 'High'
        ) AS high_incidents,

        COUNT(*) FILTER (
            WHERE i.severity = 'Medium'
        ) AS medium_incidents,

        COUNT(*) FILTER (
            WHERE i.severity = 'Low'
        ) AS low_incidents,

        ROUND(
            AVG(
                EXTRACT(
                    EPOCH FROM (
                        i.end_time - i.start_time
                    )
                ) / 60
            ),
            2
        ) AS avg_resolution_minutes

    FROM incidents i

    JOIN sites s
        ON i.site_id = s.site_id

    GROUP BY
        s.site_id,
        s.site_name,
        s.region,
        s.district;
    """

    with engine.begin() as connection:
        connection.execute(text(sql))

    print("gold_incident_summary created.")


def create_gold_network_intelligence():

    print("Creating gold_network_intelligence...")

    sql = """
    DROP TABLE IF EXISTS gold_network_intelligence;

    CREATE TABLE gold_network_intelligence AS

    SELECT
        p.site_id,
        p.site_name,
        p.region,
        p.district,

        p.measurement_date,

        p.measurement_count,

        p.avg_traffic_mb,
        p.avg_latency_ms,
        p.avg_packet_loss_pct,
        p.avg_signal_strength_dbm,
        p.avg_availability_pct,

        COALESCE(
            i.total_incidents,
            0
        ) AS total_incidents,

        COALESCE(
            i.critical_incidents,
            0
        ) AS critical_incidents,

        COALESCE(
            i.high_incidents,
            0
        ) AS high_incidents,

        COALESCE(
            i.avg_resolution_minutes,
            0
        ) AS avg_resolution_minutes,

        CASE
            WHEN
                p.avg_availability_pct < 95
                OR p.avg_packet_loss_pct > 5
                OR p.avg_latency_ms > 70
            THEN 'Critical'

            WHEN
                p.avg_availability_pct < 98
                OR p.avg_packet_loss_pct > 2
                OR p.avg_latency_ms > 40
            THEN 'Warning'

            ELSE 'Healthy'
        END AS network_health

    FROM gold_site_daily_performance p

    LEFT JOIN gold_incident_summary i
        ON p.site_id = i.site_id;
    """

    with engine.begin() as connection:
        connection.execute(text(sql))

    print("gold_network_intelligence created.")


def run_gold():

    create_gold_site_daily_performance()
    create_gold_equipment_health()
    create_gold_incident_summary()
    create_gold_network_intelligence()


if __name__ == "__main__":
    run_gold()
