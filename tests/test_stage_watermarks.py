from src.ingestion.watermark import (
    get_watermark,
    update_watermark,
)
from src.transformation.gold_incremental import (
    get_gold_watermark,
)


def test_stage_watermark_functions_are_callable():
    """ARRANGE, ACT & ASSERT: Verifies the multi-stage watermark management hooks are fully callable."""
    assert callable(get_watermark)
    assert callable(update_watermark)
    assert callable(get_gold_watermark)
