from src.transformation.raw_to_silver import (
    get_new_raw_measurements,
    promote_incremental_raw_to_silver,
)
from src.ingestion.incremental import (
    get_latest_raw_id,
    advance_processing_watermark,
)


def test_incremental_functions_are_callable():
    """ARRANGE, ACT & ASSERT: Verifies the incremental extraction and promotion functions are fully callable."""
    assert callable(get_new_raw_measurements)
    assert callable(promote_incremental_raw_to_silver)
    assert callable(get_latest_raw_id)
    assert callable(advance_processing_watermark)
