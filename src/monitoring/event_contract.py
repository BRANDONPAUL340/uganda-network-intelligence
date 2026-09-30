"""
Uganda Network Intelligence Platform — Event Contract Validation Engine
Centrally validates envelope and payload data structures before database storage [INDEX].
"""
import sys
from pathlib import Path
from datetime import datetime

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

ALLOWED_EVENT_TYPES = {
    "PIPELINE_STARTED", "PIPELINE_COMPLETED", "PIPELINE_FAILED",
    "QUALITY_CHECK_PASSED", "QUALITY_CHECK_FAILED",
    "INCIDENT_CREATED", "INCIDENT_RESOLVED",
    "NOTIFICATION_SENT", "NOTIFICATION_FAILED"
}

SUPPORTED_EVENT_VERSIONS = {
    "QUALITY_CHECK_FAILED": {1, 2},
    "PIPELINE_STARTED": {1},
    "PIPELINE_COMPLETED": {1},
    "PIPELINE_FAILED": {1}
}

ALLOWED_QUALITY_STATUSES = {"PASS", "WARNING", "FAIL"}
QUALITY_CHECK_FAILED_V1_REQUIRED = {"check_name", "status", "failed_records", "message"}
QUALITY_CHECK_FAILED_V2_REQUIRED = {"check", "severity", "error_description"}


def validate_event_envelope(event: dict, errors: list) -> None:
    """Stage 1 & 2: Asserts presence and explicit data type requirements for envelope metadata fields [INDEX]."""
    required_envelope_fields = ["event_id", "event_type", "event_version", "run_id", "event_time", "producer", "payload"]
    for field in required_envelope_fields:
        if field not in event:
            errors.append(f"Envelope Contract Breach: Missing tracking field '{field}'")
            return

    if not isinstance(event["event_type"], str):
        errors.append("Envelope Contract Breach: 'event_type' data type must be a string text definition.")
    elif event["event_type"] not in ALLOWED_EVENT_TYPES:
        errors.append(f"Envelope Contract Breach: Unrecognized or unmapped event family type '{event['event_type']}'")

    if not isinstance(event["event_version"], int):
        errors.append("Envelope Contract Breach: 'event_version' data type must be an integer value.")
    else:
        if event["event_type"] in ALLOWED_EVENT_TYPES and event["event_version"] not in SUPPORTED_EVENT_VERSIONS.get(event["event_type"], set()):
            errors.append(f"Envelope Contract Breach: Version variant '{event['event_version']}' is unsupported for type '{event['event_type']}'")

    if not isinstance(event["run_id"], int) or event["run_id"] <= 0:
        errors.append("Envelope Contract Breach: 'run_id' data type must be a positive integer lineage value.")

    if not isinstance(event["payload"], dict):
        errors.append("Envelope Contract Breach: 'payload' property field must be a valid dictionary object.")

    try:
        datetime.fromisoformat(event["event_time"].replace("Z", "+00:00"))
    except Exception:
        errors.append(f"Envelope Contract Breach: 'event_time' must be a valid ISO-8601 string template.")


def validate_v1_payload(payload: dict, errors: list) -> None:
    """Stage 3 & 4: Validates payload structural keys, types, and business rules for Version 1 contracts [INDEX]."""
    missing = QUALITY_CHECK_FAILED_V1_REQUIRED - payload.keys()
    if missing:
        errors.append(f"Payload Contract Breach (V1): Missing required keys {list(missing)}")
        return

    if not isinstance(payload["check_name"], str) or not payload["check_name"].strip():
        errors.append("Payload Contract Breach (V1): 'check_name' data type must be a valid string text definition.")

    if not isinstance(payload["status"], str) or payload["status"] not in ALLOWED_QUALITY_STATUSES:
        errors.append(f"Payload Contract Breach (V1): Invalid status parameter value. Allowed: {list(ALLOWED_QUALITY_STATUSES)}")

    # 12 & 14. Enforce strict parameter bounds and business validation rules defensively [INDEX]
    if not isinstance(payload["failed_records"], int):
        errors.append("Payload Contract Breach (V1): 'failed_records' data type must be an integer.")
    else:
        if payload["failed_records"] < 0:
            errors.append("Business Validation Breach (V1): 'failed_records' baseline count parameters cannot be negative.")
        if payload["status"] == "FAIL" and payload["failed_records"] == 0:
            errors.append("Business Validation Breach (V1): Status 'FAIL' normally requires a 'failed_records' metric threshold > 0.")


def validate_v2_payload(payload: dict, errors: list) -> None:
    """Stage 3 & 4: Validates payload structural keys and types for graduated Version 2 contracts [INDEX]."""
    missing = QUALITY_CHECK_FAILED_V2_REQUIRED - payload.keys()
    if missing:
        errors.append(f"Payload Contract Breach (V2): Missing required keys {list(missing)}")
        return

    if payload["severity"] not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        errors.append(f"Payload Contract Breach (V2): Invalid severity level value '{payload['severity']}'")


def validate_event(event: dict) -> dict:
    """
    16 & 17. Centralized Validation Flow Engine: Validates envelope headers and inner payload blocks,
    returning a structured, descriptive dictionary summary of all encountered error flags [INDEX].
    """
    errors_list = []
    
    # Run heading header checks first [INDEX]
    validate_event_envelope(event, errors_list)
    if errors_list:
        return {"valid": False, "errors": errors_list}

    # Run version-specific inner payload evaluation paths
    event_type = event["event_type"]
    version = event["event_version"]
    
    if event_type == "QUALITY_CHECK_FAILED":
        if version == 1:
            validate_v1_payload(event["payload"], errors_list)
        elif version == 2:
            validate_v2_payload(event["payload"], errors_list)

    if errors_list:
        return {"valid": False, "errors": errors_list}
        
    return {"valid": True, "errors": []}


def validate_event_envelope_contract(event: dict) -> None:
    """Legacy compatibility bridge wrapper method to sustain database adapter tests [INDEX]."""
    res = validate_event(event)
    if not res["valid"]:
        raise ValueError(f"Contract Validation Failure: {res['errors'][0]}")
