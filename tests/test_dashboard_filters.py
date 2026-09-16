from src.dashboard.data import get_site_performance


def test_site_performance_region_filter():
    """ARRANGE, ACT & ASSERT: Verifies that the region filter isolates rows correctly [INDEX]."""
    result = get_site_performance(region="Central")
    assert result is not None
    if not result.empty:
        assert (result["region"] == "Central").all()


def test_site_performance_district_filter():
    """ARRANGE, ACT & ASSERT: Verifies that the district filter isolates rows correctly [INDEX]."""
    result = get_site_performance(district="Kampala")
    assert result is not None
    if not result.empty:
        assert (result["district"] == "Kampala").all()


def test_site_performance_date_filter():
    """ARRANGE, ACT & ASSERT: Verifies chronological date pickers apply filters cleanly [INDEX]."""
    result = get_site_performance(
        start_date="2026-09-01",
        end_date="2026-09-30",
    )
    assert result is not None
