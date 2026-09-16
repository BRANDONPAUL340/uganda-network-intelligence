from src.pipeline_watermarks import advance_stage_watermark


def test_advance_stage_watermark_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the unified advance_stage_watermark helper is fully callable [INDEX]."""
    assert callable(advance_stage_watermark)
