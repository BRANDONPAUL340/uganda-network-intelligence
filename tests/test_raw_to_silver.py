from src.transformation.raw_to_silver import promote_raw_to_silver


def test_promote_raw_to_silver_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the raw to silver promotional engine exists as a callable function."""
    assert callable(promote_raw_to_silver)


def test_promote_raw_to_silver_returns_accounting_shape():
    """ARRANGE, ACT & ASSERT: Verifies the promotion runner returns an operational summary dictionary [INDEX]."""
    # Act
    result = promote_raw_to_silver()
    
    # Assert
    assert isinstance(result, dict)
    assert "records_loaded" in result
    assert "records_quarantined" in result
    assert result["records_loaded"] >= 0
    assert result["records_quarantined"] >= 0
