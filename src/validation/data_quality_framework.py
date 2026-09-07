from sqlalchemy import text
from src.database import engine
from src.logger import get_logger

# Initialize package-level logger instance
logger = get_logger(__name__)


def evaluate_data_quality():
    """
    Executes a comprehensive, multi-dimensional data quality evaluation 
    across all primary database tables. 
    
    Checks across Completeness, Validity, Consistency, Uniqueness, and Referential Integrity.
    
    Returns:
        dict: A structured summary scorecard mapping tests to passed status and failed count markers.
    """
    logger.info("🎬 Starting comprehensive Enterprise Data Quality Framework analysis...")
    
    scorecard = {}
    
    # -------------------------------------------------------------------------
    # 📊 PILLAR 1: SITES QUALITY GATE CHECKS (Completeness & Validity)
    # -------------------------------------------------------------------------
    sites_sql = """
    SELECT 
        COUNT(*) FILTER (WHERE site_name IS NULL OR TRIM(site_name) = '') AS null_names,
        COUNT(*) FILTER (WHERE district IS NULL OR TRIM(district) = '') AS null_districts,
        COUNT(*) FILTER (WHERE latitude IS NOT NULL AND NOT (latitude BETWEEN -1.5 AND 4.5)) AS invalid_lat,
        COUNT(*) FILTER (WHERE longitude IS NOT NULL AND NOT (longitude BETWEEN 29.5 AND 35.5)) AS invalid_lon,
        COUNT(site_id) - COUNT(DISTINCT site_id) AS duplicate_ids
    FROM sites;
    """
    with engine.begin() as connection:
        res = connection.execute(text(sites_sql)).mappings().one()
        
        scorecard["sites_completeness"] = {
            "passed": res["null_names"] == 0 and res["null_districts"] == 0,
            "failed_count": res["null_names"] + res["null_districts"],
            "message": f"Missing names: {res['null_names']}, Missing districts: {res['null_districts']}"
        }
        scorecard["sites_geography_validity"] = {
            "passed": res["invalid_lat"] == 0 and res["invalid_lon"] == 0,
            "failed_count": res["invalid_lat"] + res["invalid_lon"],
            "message": f"Out-of-bounds Latitude: {res['invalid_lat']}, Longitude: {res['invalid_lon']} (Uganda Range)"
        }
        scorecard["sites_uniqueness"] = {
            "passed": res["duplicate_ids"] == 0,
            "failed_count": res["duplicate_ids"],
            "message": f"Duplicate primary key constraints caught: {res['duplicate_ids']}"
        }

    # -------------------------------------------------------------------------
    # 🔧 PILLAR 2: EQUIPMENT QUALITY GATE CHECKS (Completeness & Referential Integrity)
    # -------------------------------------------------------------------------
    equipment_sql = """
    SELECT 
        COUNT(*) FILTER (WHERE equipment_type IS NULL OR TRIM(equipment_type) = '') AS null_types,
        COUNT(*) FILTER (WHERE status IS NULL OR TRIM(status) = '') AS null_status,
        COUNT(*) FILTER (WHERE e.site_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM sites s WHERE s.site_id = e.site_id
        )) AS orphan_sites
    FROM equipment e;
    """
    with engine.begin() as connection:
        res = connection.execute(text(equipment_sql)).mappings().one()
        
        scorecard["equipment_completeness"] = {
            "passed": res["null_types"] == 0 and res["null_status"] == 0,
            "failed_count": res["null_types"] + res["null_status"],
            "message": f"Missing types: {res['null_types']}, Missing status: {res['null_status']}"
        }
        scorecard["equipment_referential_integrity"] = {
            "passed": res["orphan_sites"] == 0,
            "failed_count": res["orphan_sites"],
            "message": f"Equipment rows mapped to non-existent sites: {res['orphan_sites']}"
        }

    # -------------------------------------------------------------------------
    # 📡 PILLAR 3: MEASUREMENTS QUALITY GATE CHECKS (Validity & Referential Integrity)
    # -------------------------------------------------------------------------
    measurements_sql = """
    SELECT 
        COUNT(*) FILTER (WHERE traffic_mb < 0) AS negative_traffic,
        COUNT(*) FILTER (WHERE latency_ms < 0) AS negative_latency,
        COUNT(*) FILTER (WHERE NOT (packet_loss_pct BETWEEN 0 AND 100)) AS invalid_packet_loss,
        COUNT(*) FILTER (WHERE NOT (availability_pct BETWEEN 0 AND 100)) AS invalid_availability,
        COUNT(*) FILTER (WHERE m.site_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM sites s WHERE s.site_id = m.site_id
        )) AS orphan_sites,
        COUNT(*) FILTER (WHERE m.equipment_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM equipment e WHERE e.equipment_id = m.equipment_id
        )) AS orphan_equipment
    FROM measurements m;
    """
    with engine.begin() as connection:
        res = connection.execute(text(measurements_sql)).mappings().one()
        
        scorecard["measurements_validity"] = {
            "passed": (res["negative_traffic"] == 0 and res["negative_latency"] == 0 and 
                       res["invalid_packet_loss"] == 0 and res["invalid_availability"] == 0),
            "failed_count": (res["negative_traffic"] + res["negative_latency"] + 
                             res["invalid_packet_loss"] + res["invalid_availability"]),
            "message": f"Bound violations - Traffic: {res['negative_traffic']}, Latency: {res['negative_latency']}, Packet Loss: {res['invalid_packet_loss']}, Availability: {res['invalid_availability']}"
        }
        scorecard["measurements_referential_integrity"] = {
            "passed": res["orphan_sites"] == 0 and res["orphan_equipment"] == 0,
            "failed_count": res["orphan_sites"] + res["orphan_equipment"],
            "message": f"Orphan references - Missing Sites: {res['orphan_sites']}, Missing Equipment: {res['orphan_equipment']}"
        }

    # -------------------------------------------------------------------------
    # 🚨 PILLAR 4: INCIDENTS QUALITY GATE CHECKS (Completeness & Chronological Consistency)
    # -------------------------------------------------------------------------
    incidents_sql = """
    SELECT 
        COUNT(*) FILTER (WHERE severity IS NULL OR TRIM(severity) = '') AS null_severity,
        COUNT(*) FILTER (WHERE start_time IS NULL) AS null_start,
        COUNT(*) FILTER (WHERE end_time IS NOT NULL AND end_time < start_time) AS inverted_chronology,
        COUNT(*) FILTER (WHERE i.site_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM sites s WHERE s.site_id = i.site_id
        )) AS orphan_sites
    FROM incidents i;
    """
    with engine.begin() as connection:
        res = connection.execute(text(incidents_sql)).mappings().one()
        
        scorecard["incidents_completeness"] = {
            "passed": res["null_severity"] == 0 and res["null_start"] == 0,
            "failed_count": res["null_severity"] + res["null_start"],
            "message": f"Missing severity: {res['null_severity']}, Missing start timestamp: {res['null_start']}"
        }
        scorecard["incidents_consistency"] = {
            "passed": res["inverted_chronology"] == 0,
            "failed_count": res["inverted_chronology"],
            "message": f"Chronology violations (end_time before start_time): {res['inverted_chronology']}"
        }
        scorecard["incidents_referential_integrity"] = {
            "passed": res["orphan_sites"] == 0,
            "failed_count": res["orphan_sites"],
            "message": f"Incidents mapped to non-existent sites: {res['orphan_sites']}"
        }

    # Calculate global execution metrics scorecard parameters
    total_checks = len(scorecard)
    passed_checks = sum(1 for gate in scorecard.values() if gate["passed"])
    global_passed = passed_checks == total_checks
    
    logger.info(
        f"Data quality framework evaluation complete. Score: {passed_checks}/{total_checks} checks passed."
    )
    
    return {
        "global_passed": global_passed,
        "scorecode": f"{passed_checks}/{total_checks}",
        "checks": scorecard
    }


if __name__ == "__main__":
    # Test pass when executed standalone
    report = evaluate_data_quality()
    print("\n📝 DATA QUALITY FRAMEWORK SCORECARD:")
    print("=" * 60)
    print(f"Global Pipeline Passed Gate? Status = {report['global_passed']} ({report['scorecode']})")
    print("=" * 60)
    for check_name, info in report["checks"].items():
        status_marker = "✅ PASS" if info["passed"] else "❌ FAIL"
        print(f"{status_marker} | {check_name:<40} | Violations: {info['failed_count']}")
        if not info["passed"]:
            print(f"   └── ⚠️ Error Details: {info['message']}")
