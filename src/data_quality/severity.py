def determine_severity(check_name, failed_records):
    """
    Programmatically determines the appropriate multi-tier operational
    severity rating for an incoming data quality contract failure.
    """
    # 🟢 If zero validation errors are caught, default cleanly to INFO metrics tracks
    if failed_records == 0:
        return "INFO"

    # 🚨 CRITICAL SEVERITY: Core Spatial, Uniqueness, and Relational Constraints
    critical_checks = {
        "duplicate_sites",
        "invalid_latitude",
        "invalid_longitude",
        "missing_site_name",
        "orphan_equipment_sites",
        "orphan_measurement_sites",
        "orphan_measurement_equipment",
        "orphan_incident_sites",
        "orphan_incident_equipment"
    }

    if check_name in critical_checks:
        return "CRITICAL"

    # ⚠️ WARNING SEVERITY: Non-critical anomalies or boundary threshold escapes
    return "WARNING"
