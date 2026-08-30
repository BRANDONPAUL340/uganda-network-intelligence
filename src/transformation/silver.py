from sqlalchemy import text

from src.database import engine


def upgrade_silver_schemas():
    """
    Upgrade existing Silver tables without deleting existing data.

    Ensures:
    - ingested_at tracking columns exist
    - measurement_id is protected by a primary key
    """

    print("Checking and upgrading Silver schemas...")

    alter_cols_sql = """
    ALTER TABLE silver_measurements
    ADD COLUMN IF NOT EXISTS
        ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

    ALTER TABLE silver_network_health
    ADD COLUMN IF NOT EXISTS
        ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """

    check_measurement_pk_sql = """
    SELECT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'silver_measurements'::regclass
          AND contype = 'p'
    );
    """

    check_health_pk_sql = """
    SELECT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'silver_network_health'::regclass
          AND contype = 'p'
    );
    """

    add_measurement_pk_sql = """
    ALTER TABLE silver_measurements
    ADD PRIMARY KEY (measurement_id);
    """

    add_health_pk_sql = """
    ALTER TABLE silver_network_health
    ADD PRIMARY KEY (measurement_id);
    """

    with engine.begin() as connection:

        # -------------------------------------------------
        # 1. Add tracking columns
        # -------------------------------------------------

        connection.execute(text(alter_cols_sql))

        # -------------------------------------------------
        # 2. Check Silver measurements primary key
        # -------------------------------------------------

        measurement_pk_exists = connection.execute(
            text(check_measurement_pk_sql)
        ).scalar()

        if not measurement_pk_exists:
            connection.execute(
                text(add_measurement_pk_sql)
            )
            print(
                "Primary key added to silver_measurements."
            )
        else:
            print(
                "Primary key already exists on "
                "silver_measurements."
            )

        # -------------------------------------------------
        # 3. Check Silver health primary key
        # -------------------------------------------------

        health_pk_exists = connection.execute(
            text(check_health_pk_sql)
        ).scalar()

        if not health_pk_exists:
            connection.execute(
                text(add_health_pk_sql)
            )
            print(
                "Primary key added to "
                "silver_network_health."
            )
        else:
            print(
                "Primary key already exists on "
                "silver_network_health."
            )

    print("Silver schemas are ready.")


def load_silver_measurements():
    """
    Incrementally load new measurements into Silver.

    Existing measurement IDs are ignored.
    Returns the number of newly inserted records.
    """

    print("Loading new measurements into Silver...")

    sql = """
    INSERT INTO silver_measurements (
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
        ingested_at
    )

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
        m.availability_pct,

        m.ingested_at

    FROM measurements m

    JOIN sites s
        ON m.site_id = s.site_id

    JOIN equipment e
        ON m.equipment_id = e.equipment_id

    ON CONFLICT (measurement_id)
    DO NOTHING;
    """

    with engine.begin() as connection:

        result = connection.execute(text(sql))

        records_loaded = result.rowcount

    print(
        f"New Silver measurements loaded: "
        f"{records_loaded}"
    )

    return records_loaded


def load_silver_network_health():
    """
    Incrementally create network health records
    from Silver measurements.

    Returns the number of newly inserted records.
    """

    print("Loading network health...")

    sql = """
    INSERT INTO silver_network_health (
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
        health_status,
        ingested_at
    )

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

        END AS health_status,

        ingested_at

    FROM silver_measurements

    ON CONFLICT (measurement_id)
    DO NOTHING;
    """

    with engine.begin() as connection:

        result = connection.execute(text(sql))

        records_loaded = result.rowcount

    print(
        f"New network-health records loaded: "
        f"{records_loaded}"
    )

    return records_loaded


def run_silver():
    """
    Execute the complete Silver layer.
    """

    print("\n--- SILVER LAYER ---")

    # Step 1: Ensure Silver schemas are ready
    upgrade_silver_schemas()

    # Step 2: Incrementally load measurements
    measurements_loaded = load_silver_measurements()

    # Step 3: Generate health records
    health_loaded = load_silver_network_health()

    return {
        "measurements_loaded": measurements_loaded,
        "health_loaded": health_loaded
    }


if __name__ == "__main__":
    run_silver()