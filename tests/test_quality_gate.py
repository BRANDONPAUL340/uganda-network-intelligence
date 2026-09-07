from src.data_quality.quality_gate import build_quality_checks, run_quality_gate


def test_measurement_quality_gate_keys_exist():
    """
    ARRANGE, ACT & ASSERT: Verifies that our proactive quality gate scanner 
    incorporates all expected core network and dimensional checks.
    """
    checks = build_quality_checks()
    check_names = {c["name"] for check in checks for c in [check]}

    assert "negative_traffic" in check_names
    assert "negative_latency" in check_names
    assert "invalid_packet_loss" in check_names
    assert "invalid_availability" in check_names
    assert "orphan_measurement_sites" in check_names
    assert "orphan_measurement_equipment" in check_names


def test_quality_gate_is_callable():
    """
    ARRANGE, ACT & ASSERT: Verifies that our global quality gate orchestrator 
    is compiled and callable inside the continuous integration suite.
    """
    assert callable(run_quality_gate)
