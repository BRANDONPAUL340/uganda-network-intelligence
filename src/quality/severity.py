# 🛡️ Quality Rule Configuration: Strict Perimeter Processing Blocks
critical_checks = {
    "duplicate_sites",
    "missing_measurement_id",
    "invalid_site_reference",
    "invalid_equipment_reference",
    "duplicate_raw_measurements",  # 🏗️ Added: Trap ingestion dups immediately as CRITICAL
}
