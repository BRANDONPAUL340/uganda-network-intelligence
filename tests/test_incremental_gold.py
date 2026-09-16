from src.transformation.gold import (
    get_affected_site_dates,
    refresh_gold_site_daily_incremental,
)


def test_incremental_gold_functions_are_callable():
    """ARRANGE, ACT & ASSERT: Verifies the incremental target selection and merge engines are fully callable."""
    assert callable(get_affected_site_dates)
    assert callable(refresh_gold_site_daily_incremental)
