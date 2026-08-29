import pandas as pd

from src.database import engine
from src.ingestion.validate_measurements import validate_measurements


FILE_PATH = "data/measurements.csv"


def get_equipment():

    query = """
        SELECT
            e.equipment_id,
            s.site_id,
            s.site_name,
            s.district,
            e.equipment_type,
            e.manufacturer,
            e.model
        FROM equipment e
        JOIN sites s
            ON e.site_id = s.site_id;
    """

    return pd.read_sql(query, engine)


def load_measurements():

    print("Reading measurements CSV...")

    df = pd.read_csv(FILE_PATH)

    print(f"Records found: {len(df)}")

    print("Running data-quality checks...")

    errors = validate_measurements(df)

    if errors:

        print("DATA QUALITY FAILED")

        for error in errors:
            print(f"- {error}")

        return

    print("DATA QUALITY PASSED")

    # 🛠️ TRANSFORMATION STAGE: Convert raw string text into real database TIMESTAMP types
    print("Transforming text timestamps into real datetime objects...")
    df["measured_at"] = pd.to_datetime(df["measured_at"])

    print("Looking up equipment IDs...")

    equipment = get_equipment()

    df = df.merge(
        equipment,
        on=[
            "site_name",
            "district",
            "equipment_type",
            "manufacturer",
            "model",
        ],
        how="left"
    )

    missing_equipment = df[
        df["equipment_id"].isnull()
    ]

    if not missing_equipment.empty:

        print("EQUIPMENT LOOKUP FAILED")

        for _, row in missing_equipment.iterrows():

            print(
                f"- Equipment not found: "
                f"{row['site_name']} / "
                f"{row['equipment_type']} / "
                f"{row['manufacturer']} / "
                f"{row['model']}"
            )

        return

    print("All equipment successfully matched.")

    measurements = df[
        [
            "equipment_id",
            "site_id",
            "measured_at",
            "traffic_mb",
            "latency_ms",
            "packet_loss_pct",
            "signal_strength_dbm",
            "availability_pct",
        ]
    ]

    print("Loading measurements into PostgreSQL...")

    measurements.to_sql(
        "measurements",
        engine,
        if_exists="append",
        index=False
    )

    print(
        f"Successfully loaded "
        f"{len(measurements)} measurements."
    )


if __name__ == "__main__":
    load_measurements()
