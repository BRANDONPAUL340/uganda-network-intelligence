import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load hidden parameters from your secure .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Unified connection URL using modern psycopg3 syntax
DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

def test_connection():
    with engine.connect() as connection:
        # Query 1: Fetch the active connected database name
        result = connection.execute(text("SELECT current_database();"))
        database_name = result.scalar()
        print(f"Connected to database: {database_name}")

        # Query 2: Fetch the active row count from your parent dimension table
        result = connection.execute(text("SELECT COUNT(*) FROM sites;"))
        site_count = result.scalar()
        print(f"Number of sites: {site_count}")

if __name__ == "__main__":
    test_connection()
