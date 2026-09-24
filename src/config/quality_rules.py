"""
Uganda Network Intelligence Platform — Data Quality Configuration Rules Ledger
Centralized repository for managing policy boundaries and error thresholds [INDEX].
"""

QUALITY_RULES = {
    "volume_check": {
        "minimum_count": 1,
        "policy_consequence": "FAIL"  # Hard block if table runs completely empty [INDEX]
    },
    "null_site_id": {
        "warning_threshold_pct": 1.0,  # Warning banner if up to 1% nulls tracked [INDEX]
        "failure_threshold_pct": 5.0,  # Hard block if null density passes 5% [INDEX]
        "policy_consequence": "FAIL"
    },
    "duplicate_records": {
        "warning_threshold_pct": 0.2,
        "failure_threshold_pct": 1.0,
        "policy_consequence": "FAIL"
    },
    "valid_ranges": {
        "warning_threshold_pct": 0.1,
        "failure_threshold_pct": 1.0,
        "policy_consequence": "FAIL"
    },
    "data_freshness": {
        "warning_threshold_hours": 12.0, # Alert if last packet is > 12h old [INDEX]
        "failure_threshold_hours": 24.0, # Escalation if last packet is > 24h old [INDEX]
        "policy_consequence": "WARNING"  # Non-blocking, registers warning alert [INDEX]
    }
}
