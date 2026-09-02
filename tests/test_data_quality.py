from sqlalchemy import text

from src.database import engine
from src.data_quality.checks import (
    check_sites_for_nulls,
    check_duplicate_sites,
    check_measurement_ranges,
    check_orphan_equipment,
    check_orphan_measurements,
    check_incident_dates,
)


def test_sites_have_no_required_nulls():
    """Assert that no required reference fields contain invalid NULL states."""
    assert check_sites_for_nulls() is True


def test_no_duplicate_sites():
    """Assert that no cell tower possesses duplicate records in the same district."""
    assert check_duplicate_sites() is True


def test_measurements_are_valid():
    """Assert that telemetry parameters conform strictly to realistic operational limits."""
    assert check_measurement_ranges() is True


def test_no_orphan_equipment():
    """Assert that every equipment record links to a valid parent site identifier."""
    assert check_orphan_equipment() is True


def test_no_orphan_measurements():
    """Assert that every telemetry log points to a valid site and equipment piece."""
    assert check_orphan_measurements() is True


def test_incident_dates_are_valid():
    """Assert that no incident contains an impossible negative temporal duration."""
    assert check_incident_dates() is True


def test_sites_exist():
    """Verify that the sites reference dataset is populated and active."""
    sql = "SELECT COUNT(*) FROM sites;"
    with engine.connect() as connection:
        count = connection.execute(text(sql)).scalar()
    assert count > 0


def test_equipment_exist():
    """Verify that the equipment hardware dataset is populated and active."""
    sql = "SELECT COUNT(*) FROM equipment;"
    with engine.connect() as connection:
        count = connection.execute(text(sql)).scalar()
    assert count > 0


def test_measurements_exist():
    """Verify that the raw measurements staging ledger is populated and active."""
    sql = "SELECT COUNT(*) FROM measurements;"
    with engine.connect() as connection:
        count = connection.execute(text(sql)).scalar()
    assert count > 0
