import pytest
from src.contract_validator import (
    load_contract,
    validate_columns,
)


def test_measurements_contract_loads():
    """
    ARRANGE, ACT & ASSERT: Verifies that our parser accurately decodes 
    the measurements metadata JSON contract blueprint from disk.
    """
    contract = load_contract("measurements")
    assert contract["dataset"] == "measurements"


def test_measurements_required_columns():
    """
    ARRANGE, ACT & ASSERT: Verifies that a structurally complete column listing 
    evaluates cleanly against the measurements data contract.
    """
    columns = [
        "measurement_id",
        "equipment_id",
        "site_id",
        "measured_at",
    ]
    assert validate_columns("measurements", columns)


def test_sites_contract_loads():
    """
    ARRANGE, ACT & ASSERT: Verifies that our parser accurately decodes 
    the sites dimension metadata contract blueprint from disk.
    """
    contract = load_contract("sites")
    assert contract["dataset"] == "sites"


def test_missing_required_column_is_rejected():
    """
    ARRANGE, ACT & ASSERT: Deliberately passes a broken schema missing the 
    mandatory site_id field attribute to verify that the validation firewall 
    trips immediately, raising a ValueError.
    """
    with pytest.raises(ValueError):
        validate_columns(
            "measurements",
            [
                "measurement_id",
                "equipment_id",
                "measured_at",
            ],
        )
