from sqlalchemy import create_engine

from src.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    validate_config,
)

# 🚨 Validation Gate: Crash instantly if the boot environment lacks critical credentials
validate_config()

# 🛠️ Programmatically construct the high-availability connection URL string
# Utilizing psycopg2 to bridge the low-level binary network connection layer to PostgreSQL
DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Initialize the shared connection engine adapter pool
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # 🛡️ Defensive: Automatically runs a quick health check before sending queries
)
