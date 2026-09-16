from src.dashboard.data import get_network_summary


def test_network_summary_returns_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies that the network summary function returns a valid dataframe [INDEX]."""
    result = get_network_summary()
    assert result is not None


def test_network_summary_has_expected_columns():
    """ARRANGE, ACT & ASSERT: Verifies that the summary dataframe includes all mandatory columns [INDEX]."""
    result = get_network_summary()

    expected_columns = {
        "total_sites",
        "total_measurements",
        "avg_traffic_mb",
        "avg_latency_ms",
        "avg_packet_loss_pct",
        "avg_availability_pct",
    }

    assert expected_columns.issubset(result.columns)
