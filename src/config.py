import os

from dotenv import load_dotenv

# 🔍 Locate, decrypt, and load local environment key-value pairs into system memory
load_dotenv()

# Extract database parameters with robust default fallbacks
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "network_intelligence")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Extract operational pipeline metadata fields
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "uganda_network_intelligence")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def validate_config():
    """
    Evaluates system memory to ensure all critical environment parameters 
    are populated before allowing execution.
    """
    required = {
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_NAME": DB_NAME,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
        "PIPELINE_NAME": PIPELINE_NAME,
    }

    missing = [key for key, value in required.items() if not value]

    if missing:
        raise RuntimeError(
            "Missing required configuration properties: " + ", ".join(missing)
        )


def get_database_url():
    """
    Build the PostgreSQL SQLAlchemy connection URL dynamically.
    Fails fast if the environment lacks a valid password configuration.
    """
    # 🚨 Force strict validation checklist evaluation before returning connection string
    validate_config()

    # 🛠️ Programmatically construct the connection string pattern using psycopg2 binary drivers
    return (
        f"postgresql+psycopg2://"
        f"{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}"
        f"/{DB_NAME}"
    )
