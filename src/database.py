import os
from sqlalchemy import create_engine
from src.config import DATABASE_URL
from src.logger import get_logger

logger = get_logger(__name__)

logger.info("Initializing production database connection pool using centralized environment configuration...")

# 🚀 Initialize engine with centralized credentials and pool properties
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
