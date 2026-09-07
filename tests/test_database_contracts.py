from src.contract_validator import (
    validate_database_table,
)


def test_measurements_database_contract():
    """
    ARRANGE, ACT & ASSERT: Asserts that the physical measurements table schema 
    on disk incorporates all mandatory contract columns.
    """
    assert validate_database_table("measurements")


def test_sites_database_contract():
    """
    ARRANGE, ACT & ASSERT: Asserts that the physical sites dimension schema 
    on disk incorporates all mandatory contract columns.
    """
    assert validate_database_table("sites")


def test_equipment_database_contract():
    """
    ARRANGE, ACT & ASSERT: Asserts that the physical equipment dimension schema 
    on disk incorporates all mandatory contract columns.
    """
    assert validate_database_table("equipment")


def test_incidents_database_contract():
    """
    ARRANGE, ACT & ASSERT: Asserts that the physical incidents ledger schema 
    on disk incorporates all mandatory contract columns.
    """
    assert validate_database_table("incidents")
