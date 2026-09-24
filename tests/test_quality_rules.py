from src.monitoring.quality_engine import evaluate_percentage, QUALITY_RULES


def test_duplicate_rule_passes_below_warning_threshold():
    """Asserts that failure metrics below the warning mark evaluate to PASS [INDEX]."""
    rule = QUALITY_RULES["duplicate_records"]
    status = evaluate_percentage(
        percentage=0.05,
        warning_threshold=rule["warning_threshold"],
        failure_threshold=rule["failure_threshold"]
    )
    assert status == "PASS"


def test_duplicate_rule_warns_above_warning_threshold():
    """Asserts that failure metrics between warning and failure marks evaluate to WARNING [INDEX]."""
    rule = QUALITY_RULES["duplicate_records"]
    status = evaluate_percentage(
        percentage=0.5,
        warning_threshold=rule["warning_threshold"],
        failure_threshold=rule["failure_threshold"]
    )
    assert status == "WARNING"


def test_duplicate_rule_fails_above_failure_threshold():
    """Asserts that failure metrics crossing the maximum threshold trigger a hard FAIL [INDEX]."""
    rule = QUALITY_RULES["duplicate_records"]
    status = evaluate_percentage(
        percentage=2.5,
        warning_threshold=rule["warning_threshold"],
        failure_threshold=rule["failure_threshold"]
    )
    assert status == "FAIL"
