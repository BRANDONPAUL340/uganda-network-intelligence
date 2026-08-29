import pandas as pd
from sqlalchemy import text
from src.database import engine
from src.ingestion.validate_sites import validate_sites

FILE_PATH = "data/sites.csv"

# 🔄 Add our explicit data mapping layout
SITE_TYPE_TRANSFORM_MAP = {
    "Urban": "Macro Tower",
    "Rural": "Micro Cell"
}

def get_existing_sites():
    query = text("""
        SELECT site_name, district
        FROM sites;
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        return {
            (row.site_name, row.district)
            for row in result
        }


def find_new_sites(df, existing_sites):
    mask = df.apply(
        lambda row:
        (row["site_name"], row["district"])
        not in existing_sites,
        axis=1
    )
    return df[mask]


def load_sites():
    print("Reading CSV...")
    df = pd.read_csv(FILE_PATH)
    print(f"Records found: {len(df)}")

    # 🛠️ TRANSFORM STAGE: Clean raw site type mappings before validation
    print("Transforming and cleaning raw data fields...")
    df['site_type'] = df['site_type'].map(SITE_TYPE_TRANSFORM_MAP).fillna(df['site_type'])

    print("Running data-quality checks...")
    errors = validate_sites(df)

    if errors:
        print("DATA QUALITY FAILED")
        for error in errors:
            print(f"- {error}")
        return

    print("DATA QUALITY PASSED")

    existing_sites = get_existing_sites()
    new_sites = find_new_sites(df, existing_sites)

    print(f"Existing sites: {len(df) - len(new_sites)}")
    print(f"New sites: {len(new_sites)}")

    if new_sites.empty:
        print("No new sites to load.")
        return

    print("Loading new sites into PostgreSQL...")
    new_sites.to_sql(
        "sites",
        engine,
        if_exists="append",
        index=False
    )
    print(f"Successfully loaded {len(new_sites)} new sites.")


if __name__ == "__main__":
    load_sites()
