from src.ingestion.raw_loader import load_raw_records
from src.ingestion.run_ingestion import ingest_csv, ingest_api


def test_raw_loader_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the core batch raw loader can be called."""
    assert callable(load_raw_records)


def test_csv_ingestion_runner_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the CSV ingestion entry point exists."""
    assert callable(ingest_csv)


def test_api_ingestion_runner_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the API ingestion entry point exists."""
    assert callable(ingest_api)
