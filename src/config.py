import os

from dotenv import load_dotenv


load_dotenv()


DATABASE_HOST = os.getenv(
    "DATABASE_HOST",
    "localhost"
)

DATABASE_PORT = os.getenv(
    "DATABASE_PORT",
    "5432"
)

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "network_intelligence"
)

DATABASE_USER = os.getenv(
    "DATABASE_USER",
    "postgres"
)

DATABASE_PASSWORD = os.getenv(
    "DATABASE_PASSWORD", "tech"
)


if not DATABASE_PASSWORD:

    raise RuntimeError(
        "DATABASE_PASSWORD is not configured. "
        "Please set it in the .env file."
    )