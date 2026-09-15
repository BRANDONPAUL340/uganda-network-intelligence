import logging
from datetime import date

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {
    "measurement_id",
    "site_id",
    "equipment_id",
    "measurement_date",
    "traffic_mb",
    "latency_ms",
    "packet_loss_pct",
    "signal_strength_dbm",
    "availability_pct",
}


def validate_api_record(record):
    """Audits a single dictionary record payload for JSON API compliance."""
    missing_fields = REQUIRED_FIELDS - record.keys()
    if missing_fields:
        error_msg = f"API payload validation breach. Missing fields: {sorted(missing_fields)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    return record


def normalize_api_record(record):
    """Validates and enforces strict type alignment over an incoming API record."""
    validate_api_record(record)
    
    normalized = dict(record)
    try:
        normalized["measurement_id"] = int(normalized["measurement_id"])
        normalized["site_id"] = int(normalized["site_id"])
        normalized["equipment_id"] = int(normalized["equipment_id"])
        normalized["measurement_date"] = date.fromisoformat(normalized["measurement_date"])
        normalized["traffic_mb"] = float(normalized["traffic_mb"])
        normalized["latency_ms"] = float(normalized["latency_ms"])
        normalized["packet_loss_pct"] = float(normalized["packet_loss_pct"])
        normalized["signal_strength_dbm"] = float(normalized["signal_strength_dbm"])
        normalized["availability_pct"] = float(normalized["availability_pct"])
    except (ValueError, TypeError) as e:
        error_msg = f"API record serialization error due to data type mismatch: {str(e)}"
        logger.error(error_msg)
        raise TypeError(error_msg)

    return normalized
