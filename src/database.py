import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


# Securely extract key configurations from local computer system arrays
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set."
    )


# Establish our high-performance relational connection pool
engine = create_engine(DATABASE_URL)
