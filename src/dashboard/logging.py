import logging
import sys

# Configure a structured logging format specific to the frontend dashboard workspace context
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | [DASHBOARD] | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("uganda_network_dashboard")


def get_dashboard_logger() -> logging.Logger:
    """
    Returns the standardized, stream-buffered logger instance for the 
    containerized Streamlit operations interface [INDEX].
    """
    return logger

