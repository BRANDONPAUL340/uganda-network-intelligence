import logging
from pathlib import Path

# Establish a persistent folder on disk for application telemetry records
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"


def get_logger(name="uganda_network_intelligence"):
    """
    Spins up or retrieves a context-specific logger instance hardwired to 
    stream simultaneously to the terminal window and a persistent log file.
    """
    logger = logging.getLogger(name)

    # 🛡️ Defensive Guard: Prevents registering duplicate stream handlers if called repeatedly
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # ⏳ Structured: Chronological timestamps coupled with explicit severity levels
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # 💾 Target 1: Long-term append-only ledger file on disk
    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # 🖥️ Target 2: Real-time visual terminal display stream
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Bind handlers to the central tracking module
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
