from datetime import date
from src.ingestion.api_loader import normalize_api_record


def test_normalize_api_record():
    """
    ARRANGE, ACT & ASSERT: Feeds raw string API attributes to the normalizer module
    and verifies fields successfully serialize into native Python types.
    """
    record = {
        "measurement_id": "2001",
        "site_id": "1",
        "equipment_id": "1",
        "measurement_date": "2026-09-02",
        "traffic_mb": "15000.5",
        "latency_ms": "25.5",
        "packet_loss_pct": "0.5",
        "signal_strength_dbm": "-60.0",
        "availability_pct": "99.5",
    }

    result = normalize_api_record(record)

    assert result["measurement_id"] == 2001
    assert result["site_id"] == 1
    assert result["equipment_id"] == 1
    assert result["measurement_date"] == date(2026, 9, 2)
    assert result["traffic_mb"] == 15000.5
    assert result["latency_ms"] == 25.5
