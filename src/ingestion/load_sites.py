import pandas as pd
from sqlalchemy import text
from src.database import engine
from src.ingestion.validate_sites import validate_sites

FILE_PATH = "data/sites.csv"
SITE_TYPE_TRANSFORM_MAP = {"Urban": "Macro Tower", "Rural": "Micro Cell"}

def load_sites():
    print("Reading CSV...")
    df = pd.read_csv(FILE_PATH)
    print(f"Records found: {len(df)}")

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
    print("Loading data into PostgreSQL safely (Idempotent loop)...")
    
    inserted_count = 0
    skipped_count = 0

    # Establish an explicit relational execution session block
    with engine.begin() as connection:
        for _, row in df.iterrows():
            # 🔍 First check if this specific site name is already stored in the DB
            check_query = text("SELECT COUNT(*) FROM sites WHERE site_name = :site_name;")
            exists = connection.execute(check_query, {"site_name": row["site_name"]}).scalar()

            if exists == 0:
                # If rowcount equals 0, it's safe to append this unique record
                insert_query = text("""
                    INSERT INTO sites (site_name, region, district, latitude, longitude, site_type, status)
                    VALUES (:site_name, :region, :district, :latitude, :longitude, :site_type, :status);
                """)
                connection.execute(insert_query, {
                    "site_name": row["site_name"],
                    "region": row["region"],
                    "district": row["district"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "site_type": row["site_type"],
                    "status": row["status"]
                })
                inserted_count += 1
            else:
                skipped_count += 1

    print(f"🎉 INGESTION COMPLETE: Added {inserted_count} new sites. Safely skipped {skipped_count} existing duplicates.")

if __name__ == "__main__":
    load_sites()
