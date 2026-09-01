from sqlalchemy import create_engine
from src.config import (
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_NAME,
    DATABASE_USER,
    DATABASE_PASSWORD,
)

# 🛠️ Programmatically construct the encrypted cluster network gateway endpoint URL
DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DATABASE_USER}:"
    f"{DATABASE_PASSWORD}@"
    f"{DATABASE_HOST}:"
    f"{DATABASE_PORT}/"
    f"{DATABASE_NAME}"
)

# Initialize the shared, high-availability engine pool adapter connection link
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # 🛡️ Defensive: Automatically checks connection health before running queries
)
