"""
Uganda Network Intelligence Platform — Event Contract Enforcement Engine
Defensively validates message envelopes against required metadata fields [INDEX].
"""
import sys
from pathlib import Path
from datetime import datetime

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def validate_event_envelope_contract(event: dict) -> None:
    """
    Enforces the structural core event contract [INDEX]. 
    Raises KeyErrors or ValueErrors if required parameters are missing or malformed.
    """
    # 1. Assert required top-level structural envelope attributes exist [INDEX]
    required_fields = ["event_id", "event_type", "event_version", "run_id", "event_time", "producer", "payload"]
    for field in required_fields:
        if field not in event:
            raise KeyError(f"Contract Broken: Missing required envelope metadata field token: '{field}'")

    # 2. Enforce explicit value validation rules defensively [INDEX]
    if not isinstance(event["run_id"], int) or event["run_id"] <= 0:
        raise ValueError(f"Contract Broken: 'run_id' attribute must be a positive integer. Received: {event['run_id']}")

    if not isinstance(event["payload"], dict):
        raise ValueError("Contract Broken: 'payload' property parameter field must be a valid structured dictionary.")

    # 3. Verify temporal format conformance (Must comply with ISO-8601 strings) [INDEX]
    try:
        datetime.fromisoformat(event["event_time"].replace("Z", "+00:00"))
    except Exception:
        raise ValueError(f"Contract Broken: 'event_time' stamp must be a valid ISO-8601 string template. Received: {event['event_time']}")
