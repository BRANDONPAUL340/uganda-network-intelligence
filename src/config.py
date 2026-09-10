import os
from pathlib import Path
from dotenv import load_dotenv

# Identify workspace base folder limits
BASE_DIR = Path(__file__).resolve().parent.parent

# Explicitly search for and load the .env configuration properties ledger
load_dotenv(dotenv_path=BASE_DIR / ".env")

# 🚀 Primary Configuration Exposing Matrices
ENVIRONMENT = os.getenv("ENV", "development").lower()
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "uganda_network_intel")

# Enforce a strict warning perimeter if secrets are completely missing
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "❌ Critical Configuration Error: DATABASE_URL is not set in the environment. "
        "Please check your local .env file profile parameters."
    )
