from src.transformation.gold import (
    get_affected_site_dates_from_silver,
    refresh_gold_from_silver_incremental,
)


def test_incremental_gold_functions_are_callable():
    """ARRANGE, ACT & ASSERT: Verifies the incremental staging target selection and merge engines are fully callable."""
    assert callable(get_affected_site_dates_from_silver)
    assert callable(refresh_gold_from_silver_incremental)
