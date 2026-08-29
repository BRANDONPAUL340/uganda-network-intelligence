import pandas as pd

from src.database import engine
from src.ingestion.validate_incidents import validate_incidents


FILE_PATH = "data/incidents.csv"


def get_equipment():

    query = """
        SELECT
            e.equipment_id,
            e.site_id,
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


def load_incidents():

    print("Reading incidents CSV...")

    df = pd.read_csv(FILE_PATH)

    print(f"Records found: {len(df)}")

    print("Running data-quality checks...")

    errors = validate_incidents(df)

    if errors:

        print("DATA QUALITY FAILED")

        for error in errors:
            print(f"- {error}")

        return

    print("DATA QUALITY PASSED")

    # 🛠️ TRANSFORMATION STAGE: Convert text timestamps into real datetime objects in-place
    print("Transforming text timestamps into real datetime objects...")
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

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

    incidents = df[
        [
            "site_id",
            "equipment_id",
            "incident_type",
            "severity",
            "start_time",
            "end_time",
            "status",
            "description",
        ]
    ]

    print("Loading incidents into PostgreSQL...")

    incidents.to_sql(
        "incidents",
        engine,
        if_exists="append",
        index=False
    )

    print(
        f"Successfully loaded "
        f"{len(incidents)} incidents."
    )


if __name__ == "__main__":
    load_incidents()
