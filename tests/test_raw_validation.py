from src.quality.raw_validation import (
    check_raw_measurement_count,
    check_raw_null_measurement_ids,
    check_raw_invalid_measurements,
    check_raw_missing_site_reference,
    check_raw_missing_equipment_reference,
    check_raw_duplicates,
    run_raw_quality_checks,
)


def test_raw_quality_functions_are_callable():
    """ARRANGE, ACT & ASSERT: Verifies all raw audit modules are callable functions."""
    assert callable(check_raw_measurement_count)
    assert callable(check_raw_null_measurement_ids)
    assert callable(check_raw_invalid_measurements)
    assert callable(check_raw_missing_site_reference)
    assert callable(check_raw_missing_equipment_reference)
    assert callable(check_raw_duplicates)
    assert callable(run_raw_quality_checks)
