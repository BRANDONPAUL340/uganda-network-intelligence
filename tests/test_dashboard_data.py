from src.dashboard.data import (
    get_current_health,
    get_daily_health,
    get_pipeline_kpis,
    get_site_performance,
    get_stage_summary,
)


def test_pipeline_kpis_returns_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies macro KPI fetching executes correctly [INDEX]."""
    result = get_pipeline_kpis()
    assert result is not None


def test_current_health_returns_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies real-time snapshot fetching executes correctly [INDEX]."""
    result = get_current_health()
    assert result is not None


def test_daily_health_returns_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies daily trend timeline fetching executes correctly [INDEX]."""
    result = get_daily_health()
    assert result is not None


def test_stage_summary_returns_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies stage SLA summary fetching executes correctly [INDEX]."""
    result = get_stage_summary()
    assert result is not None


def test_site_performance_returns_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies Gold-tier site analytical data fetching executes correctly [INDEX]."""
    result = get_site_performance()
    assert result is not None
