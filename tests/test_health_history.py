from src.monitoring.health import HealthStatus
from src.monitoring.history import save_health_snapshot


def test_health_history_module_exists():
    """ARRANGE, ACT & ASSERT: Verifies that the snapshot writer engine is fully callable [INDEX]."""
    assert callable(save_health_snapshot)


def test_health_status_values():
    """ARRANGE, ACT & ASSERT: Verifies that the string enums map to the correct uppercase statuses [INDEX]."""
    assert HealthStatus.HEALTHY.value == "HEALTHY"
    assert HealthStatus.WARNING.value == "WARNING"
    assert HealthStatus.CRITICAL.value == "CRITICAL"
    assert HealthStatus.UNKNOWN.value == "UNKNOWN"
