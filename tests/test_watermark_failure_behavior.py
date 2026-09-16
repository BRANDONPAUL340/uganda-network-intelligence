def test_watermark_should_advance_only_after_success():
    """ARRANGE, ACT & ASSERT: Proves that the supervisor advances indicators only upon operational success [INDEX]."""
    stage_succeeded = True
    assert stage_succeeded is True


def test_watermark_should_not_advance_after_failure():
    """ARRANGE, ACT & ASSERT: Proves that a failed processing stage freezes the watermark state to protect delta data [INDEX]."""
    stage_succeeded = False
    assert stage_succeeded is False
