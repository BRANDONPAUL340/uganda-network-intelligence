import os
from dotenv import load_dotenv

# Load environment variable configurations from a local .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Core application configuration
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")
PIPELINE_NAME = os.getenv(
    "PIPELINE_NAME",
    "uganda_network_intelligence",
)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


# ---------------------------------------------------------------------------
# Network health thresholds
# ---------------------------------------------------------------------------

CRITICAL_AVAILABILITY_PCT = float(
    os.getenv("CRITICAL_AVAILABILITY_PCT", "95")
)

CRITICAL_PACKET_LOSS_PCT = float(
    os.getenv("CRITICAL_PACKET_LOSS_PCT", "5")
)

CRITICAL_LATENCY_MS = float(
    os.getenv("CRITICAL_LATENCY_MS", "70")
)

WARNING_AVAILABILITY_PCT = float(
    os.getenv("WARNING_AVAILABILITY_PCT", "98")
)

WARNING_PACKET_LOSS_PCT = float(
    os.getenv("WARNING_PACKET_LOSS_PCT", "2")
)

WARNING_LATENCY_MS = float(
    os.getenv("WARNING_LATENCY_MS", "40")
)


# ---------------------------------------------------------------------------
# Pipeline operational thresholds
# ---------------------------------------------------------------------------

PIPELINE_SLA_SECONDS = float(
    os.getenv("PIPELINE_SLA_SECONDS", "60")
)

MAX_DATA_FRESHNESS_DAYS = float(
    os.getenv("MAX_DATA_FRESHNESS_DAYS", "1")
)


def validate_environment() -> None:
    """
    Configuration Integrity Gate.

    Validates environment context and required runtime configuration
    before the application starts.
    """

    allowed_environments = {
        "development",
        "test",
        "production",
        "dashboard",
        "podman",
    }

    if ENVIRONMENT not in allowed_environments:
        raise ValueError(
            "CRITICAL CONFIG ERROR: Unsupported ENVIRONMENT "
            f"context value: '{ENVIRONMENT}'."
        )

    if not DATABASE_URL:
        raise ValueError(
            "CRITICAL CONFIG ERROR: DATABASE_URL variable "
            "is not configured."
        )


# Force immediate validation when configuration is imported.
validate_environment()