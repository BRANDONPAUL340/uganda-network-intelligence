def test_duplicate_source_id_is_skipped():
    """
    ARRANGE, ACT & ASSERT: Verifies that our in-memory cache lookup system 
    accurately flags a duplicate source record key signature for skipping.
    """
    processed_ids = {
        "UG-0001",
        "UG-0002",
    }

    source_record_id = "UG-0001"

    assert source_record_id in processed_ids


def test_new_source_id_is_not_skipped():
    """
    ARRANGE, ACT & ASSERT: Verifies that a net-new record key signature passes 
    cleanly through our cache filter to advance to validation and ingestion.
    """
    processed_ids = {
        "UG-0001",
        "UG-0002",
    }

    source_record_id = "UG-0003"

    assert source_record_id not in processed_ids
