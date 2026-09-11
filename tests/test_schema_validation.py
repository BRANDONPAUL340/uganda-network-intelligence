from src.data_quality.schema_validation import (
    get_table_columns,
    validate_required_columns,
    validate_schema,
)


def test_sites_table_exists():
    """
    ARRANGE, ACT & ASSERT: Queries the system schemas to confirm the sites 
    dimension table is active and contains core structural fields.
    """
    columns = get_table_columns("sites")

    assert "site_id" in columns
    assert "site_name" in columns


def test_required_columns_pass():
    """
    ARRANGE, ACT & ASSERT: Verifies that your active production database 
    fully satisfies all structural presence criteria.
    """
    errors = validate_required_columns()

    assert errors == []


def test_schema_validation_passes():
    """
    ARRANGE, ACT & ASSERT: Confirms that the end-to-end data contract check 
    evaluates to True with zero logged violations.
    """
    result = validate_schema()

    assert result["passed"] is True
    assert result["errors"] == []


def test_missing_column_is_detected(monkeypatch):
    """
    ARRANGE, ACT & ASSERT: Safely simulates a schema drift condition using 
    monkeypatch to confirm the firewall catches and logs missing fields.
    """
    from src.data_quality import schema_validation

    # 🚀 Clean & Modern: Monkeypatch handles full variable restoration automatically at exit!
    monkeypatch.setattr(
        schema_validation,
        "REQUIRED_COLUMNS",
        {
            "sites": {
                "site_id",
                "site_name",
                "this_column_does_not_exist",
            }
        },
    )

    errors = schema_validation.validate_required_columns()

    assert "Missing column: sites.this_column_does_not_exist" in errors
