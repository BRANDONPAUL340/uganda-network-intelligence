from src.ingestion.csv_loader import read_measurements_csv


def test_read_measurements_csv():
    """
    ARRANGE, ACT & ASSERT: Parses the sample cell-tower source telemetry dump
    and verifies row extraction balances and field values map accurately.
    """
    records = read_measurements_csv("data/incoming/network_measurements.csv")

    assert len(records) == 5
    assert records[0]["measurement_id"] == "1001"
    assert records[4]["measurement_id"] == "1005"
