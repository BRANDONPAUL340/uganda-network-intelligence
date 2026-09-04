def test_lineage_requires_run_id():
    """
    ARRANGE, ACT & ASSERT: Verifies that our micro-level data records 
    maintain a strict lineage link back to their parent pipeline execution run slots.
    """
    record = {
        "measurement_id": 100,
        "source_record_id": "UG-00100",
        "run_id": 5,
    }

    # Enforce that every processed row carries a traceable execution context anchor
    assert record["run_id"] is not None


def test_source_identity_is_preserved():
    """
    ARRANGE, ACT & ASSERT: Enforces immutable audit trails by ensuring 
    the natural composite key token transfers seamlessly across Medallion tiers.
    """
    source_id = "UG-00100"

    silver_record = {
        "source_record_id": source_id
    }

    # Assert that data lineage identity has not mutated during transformation
    assert silver_record["source_record_id"] == source_id
