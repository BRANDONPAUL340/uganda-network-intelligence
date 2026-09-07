def check_sites_quality(run_id):
    """
    Validates completeness, uniqueness, and geographic boundary rules for the sites dimension.
    """
    checks = [
        ("site_name_not_null", "site_name IS NULL OR TRIM(site_name) = ''"),
        ("district_not_null", "district IS NULL OR TRIM(district) = ''"),
        ("latitude_valid_range", "latitude IS NOT NULL AND NOT (latitude BETWEEN -1.5 AND 4.5)"),
        ("longitude_valid_range", "longitude IS NOT NULL AND NOT (longitude BETWEEN 29.5 AND 35.5)"),
    ]

    # Handle duplicate check independently via custom aggregate condition
    duplicate_sql = """
    SELECT COUNT(*) FROM (
        SELECT site_name FROM sites GROUP BY site_name HAVING COUNT(*) > 1
    ) t;
    """

    total_sql = "SELECT COUNT(*) FROM sites;"

    with engine.begin() as connection:
        total = connection.execute(text(total_sql)).scalar()

        # Run conditional array checks
        for check_name, condition in checks:
            count_sql = f"SELECT COUNT(*) FROM sites WHERE {condition};"
            failed = connection.execute(text(count_sql)).scalar()
            status = "PASS" if failed == 0 else "FAIL"
            record_quality_result(
                run_id=run_id, table_name="sites", check_name=check_name,
                check_type="VALIDITY" if "range" in check_name else "COMPLETENESS",
                status=status, records_checked=total, records_failed=failed,
                details=f"Evaluated field constraints for check name: {check_name}"
            )

        # Run duplicate site name scan
        failed_dups = connection.execute(text(duplicate_sql)).scalar()
        status_dups = "PASS" if failed_dups == 0 else "FAIL"
        record_quality_result(
            run_id=run_id, table_name="sites", check_name="duplicate_site_names",
            check_type="UNIQUENESS", status=status_dups, records_checked=total,
            records_failed=failed_dups, details="Scanned sites dimension space for duplicate names."
        )


def check_equipment_quality(run_id):
    """
    Validates completeness and referential integrity for the equipment dimension.
    """
    checks = [
        ("equipment_type_not_null", "equipment_type IS NULL OR TRIM(equipment_type) = ''"),
        ("equipment_status_not_null", "status IS NULL OR TRIM(status) = ''"),
        ("equipment_installation_date_valid", "installation_date IS NOT NULL AND installation_date > CURRENT_TIMESTAMP"),
    ]

    orphan_sql = """
    SELECT COUNT(*) 
    FROM equipment e 
    LEFT JOIN sites s ON e.site_id = s.site_id 
    WHERE s.site_id IS NULL;
    """

    total_sql = "SELECT COUNT(*) FROM equipment;"

    with engine.begin() as connection:
        total = connection.execute(text(total_sql)).scalar()

        for check_name, condition in checks:
            count_sql = f"SELECT COUNT(*) FROM equipment WHERE {condition};"
            failed = connection.execute(text(count_sql)).scalar()
            status = "PASS" if failed == 0 else "FAIL"
            record_quality_result(
                run_id=run_id, table_name="equipment", check_name=check_name,
                check_type="VALIDITY" if "date" in check_name else "COMPLETENESS",
                status=status, records_checked=total, records_failed=failed
            )

        # Evaluate dimension referential integrity link
        failed_orphans = connection.execute(text(orphan_sql)).scalar()
        status_orphans = "PASS" if failed_orphans == 0 else "FAIL"
        record_quality_result(
            run_id=run_id, table_name="equipment", check_name="equipment_site_fk_exists",
            check_type="REFERENTIAL_INTEGRITY", status=status_orphans,
            records_checked=total, records_failed=failed_orphans
        )


def check_incidents_quality(run_id):
    """
    Validates completeness, logical chronology consistency, and referential links for the incidents log.
    """
    checks = [
        ("incident_severity_not_null", "severity IS NULL OR TRIM(severity) = ''"),
        ("incident_type_not_null", "incident_type IS NULL OR TRIM(incident_type) = ''"),
        ("incident_chronology_consistent", "end_time IS NOT NULL AND end_time < start_time"),
    ]

    orphan_site_sql = """
    SELECT COUNT(*) FROM incidents i LEFT JOIN sites s ON i.site_id = s.site_id WHERE s.site_id IS NULL;
    """
    orphan_eq_sql = """
    SELECT COUNT(*) FROM incidents i LEFT JOIN equipment e ON i.equipment_id = e.equipment_id WHERE i.equipment_id IS NOT NULL AND e.equipment_id IS NULL;
    """

    total_sql = "SELECT COUNT(*) FROM incidents;"

    with engine.begin() as connection:
        total = connection.execute(text(total_sql)).scalar()

        for check_name, condition in checks:
            count_sql = f"SELECT COUNT(*) FROM incidents WHERE {condition};"
            failed = connection.execute(text(count_sql)).scalar()
            status = "PASS" if failed == 0 else "FAIL"
            record_quality_result(
                run_id=run_id, table_name="incidents", check_name=check_name,
                check_type="CONSISTENCY" if "chronology" in check_name else "COMPLETENESS",
                status=status, records_checked=total, records_failed=failed
            )

        # Audit incident referential integrity links
        failed_sites = connection.execute(text(orphan_site_sql)).scalar()
        status_sites = "PASS" if failed_sites == 0 else "FAIL"
        record_quality_result(
            run_id=run_id, table_name="incidents", check_name="incident_site_fk_exists",
            check_type="REFERENTIAL_INTEGRITY", status=status_sites,
            records_checked=total, records_failed=failed_sites
        )

        failed_eq = connection.execute(text(orphan_eq_sql)).scalar()
        status_eq = "PASS" if failed_eq == 0 else "FAIL"
        record_quality_result(
            run_id=run_id, table_name="incidents", check_name="incident_equipment_fk_exists",
            check_type="REFERENTIAL_INTEGRITY", status=status_eq,
            records_checked=total, records_failed=failed_eq
        )
