import os
from pathlib import Path
from dotenv import load_dotenv

# Identify workspace base folder limits safely
BASE_DIR = Path(__file__).resolve().parent.parent

# Explicitly search for and load the .env configuration properties ledger
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Primary Core Configuration Exposing Matrices
ENVIRONMENT = os.getenv("ENV", "development").lower()
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "uganda_network_intelligence")
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "❌ Critical Configuration Error: DATABASE_URL is not set in the environment. "
        "Please check your local .env file profile parameters."
    )

# 🚀 Dynamic Operational SLA Threshold Parsing Layers
CRITICAL_AVAILABILITY_PCT = float(os.getenv("CRITICAL_AVAILABILITY_PCT", "95"))
CRITICAL_PACKET_LOSS_PCT = float(os.getenv("CRITICAL_PACKET_LOSS_PCT", "5"))
CRITICAL_LATENCY_MS = float(os.getenv("CRITICAL_LATENCY_MS", "70"))

WARNING_AVAILABILITY_PCT = float(os.getenv("WARNING_AVAILABILITY_PCT", "98"))
WARNING_PACKET_LOSS_PCT = float(os.getenv("PACKET_LOSS_PCT", "2"))
WARNING_LATENCY_MS = float(os.getenv("WARNING_LATENCY_MS", "40"))
# 🚀 Operational Service Level Agreement (SLA) Targets
PIPELINE_SLA_SECONDS = float(os.getenv("PIPELINE_SLA_SECONDS", "60"))
# 🚀 Operational Ingestion Freshness Targets
MAX_DATA_FRESHNESS_DAYS = int(os.getenv("MAX_DATA_FRESHNESS_DAYS", "1"))
