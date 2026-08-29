import pandas as pd

from src.database import engine
from src.ingestion.validate_equipment import validate_equipment


FILE_PATH = "data/equipment.csv"


def get_site_ids():

    query = """
        SELECT site_id, site_name, district
        FROM sites;
    """

    sites = pd.read_sql(query, engine)

    return sites


def load_equipment():

    print("Reading equipment CSV...")

    df = pd.read_csv(FILE_PATH)

    print(f"Records found: {len(df)}")

    print("Running data-quality checks...")

    errors = validate_equipment(df)

    if errors:

        print("DATA QUALITY FAILED")

        for error in errors:
            print(f"- {error}")

        return

    print("DATA QUALITY PASSED")

    # 🛠️ TRANSFORMATION STAGE: Convert raw string text into real database DATE types
    print("Transforming string dates into database date objects...")
    df["installation_date"] = pd.to_datetime(df["installation_date"]).dt.date

    print("Looking up site IDs...")

    sites = get_site_ids()

    df = df.merge(
        sites,
        on=["site_name", "district"],
        how="left"
    )

    # Check for sites that don't exist
    missing_sites = df[df["site_id"].isnull()]

    if not missing_sites.empty:

        print("SITE LOOKUP FAILED")

        for _, row in missing_sites.iterrows():

            print(
                f"- Site not found: "
                f"{row['site_name']} / {row['district']}"
            )

        return

    print("All sites successfully matched.")

    # Select database columns
    equipment = df[
        [
            "site_id",
            "equipment_type",
            "manufacturer",
            "model",
            "installation_date",
            "status",
        ]
    ]

    print("Loading equipment into PostgreSQL...")

    equipment.to_sql(
        "equipment",
        engine,
        if_exists="append",
        index=False
    )

    print(
        f"Successfully loaded "
        f"{len(equipment)} equipment records."
    )


if __name__ == "__main__":
    load_equipment()
