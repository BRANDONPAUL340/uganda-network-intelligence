from src.monitoring.health import (
    HealthStatus,
    combine_health_statuses,
)


def test_critical_has_highest_priority():
    """ARRANGE, ACT & ASSERT: Proves that CRITICAL override inputs always dominate the matrix [INDEX]."""
    result = combine_health_statuses([
        HealthStatus.HEALTHY,
        HealthStatus.WARNING,
        HealthStatus.CRITICAL,
    ])
    assert result == HealthStatus.CRITICAL


def test_warning_is_above_healthy():
    """ARRANGE, ACT & ASSERT: Proves that WARNING status takes priority over basic HEALTHY states [INDEX]."""
    result = combine_health_statuses([
        HealthStatus.HEALTHY,
        HealthStatus.WARNING,
    ])
    assert result == HealthStatus.WARNING


def test_all_healthy():
    """ARRANGE, ACT & ASSERT: Proves that an all-clear input set returns a pure HEALTHY status [INDEX]."""
    result = combine_health_statuses([
        HealthStatus.HEALTHY,
        HealthStatus.HEALTHY,
    ])
    assert result == HealthStatus.HEALTHY


def test_empty_statuses_are_unknown():
    """ARRANGE, ACT & ASSERT: Proves that empty array parameters default to an UNKNOWN state [INDEX]."""
    result = combine_health_statuses([])
    assert result == HealthStatus.UNKNOWN
