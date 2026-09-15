from src.ingestion.watermark import (
    get_watermark,
    update_watermark,
    advance_watermark,
)


def test_watermark_functions_are_callable():
    """ARRANGE, ACT & ASSERT: Verifies the watermark management routines exist and are fully callable."""
    assert callable(get_watermark)
    assert callable(update_watermark)
    assert callable(advance_watermark)
