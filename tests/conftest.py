"""
Uganda Network Intelligence Platform — Centralized Test Harness Configuration
Implements the Test Data Factory Pattern featuring parameterized keyword overrides [INDEX].
"""
import os
import sys
from pathlib import Path
import pytest
from sqlalchemy import text
import pandas as pd
from src.database import engine

# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


def verify_active_database_safety_barrier(connection) -> None:
    """Safety Barrier: Asserts that operations run ONLY against the test database sandbox [INDEX]."""
    active_db = connection.execute(text("SELECT current_database();")).scalar()
    if active_db != "network_intelligence_test":
        raise RuntimeError(
            f"❌ CRITICAL SAFETY BREACH: Destructive test setup blocked! "
            f"Engine is pointing directly to active database catalog '{active_db}' "
            f"instead of 'network_intelligence_test'."
        )


@pytest.fixture(scope="function")
def db_connection():
    """Provides a clean pool connection handle and applies the database safety firewall [INDEX]."""
    connection = engine.connect()
    verify_active_database_safety_barrier(connection)
    yield connection
    connection.close()


# ==============================================================================
# 🏭 12 & 13. PARAMETERIZED DATA FACTORIES WITH DETERMINISTIC DEFAULTS
# ==============================================================================

def create_test_run_factory(connection, **kwargs) -> int:
    """
    12 & 13. Parameterized Run Factory: Injects a pipeline run record on disk, 
    using deterministic defaults that can be dynamically overridden by keyword args [INDEX].
    """
    # Define strict deterministic defaults [INDEX]
    defaults = {
        "pipeline_name": "pytest_deterministic_pipeline",
        "status": "SUCCESS"
    }
    # Apply keyword overrides [INDEX]
    defaults.update(kwargs)
    
    result = connection.execute(
        text(
            """
            INSERT INTO pipeline_runs (pipeline_name, status, started_at)
            VALUES (:pipeline_name, :status, CURRENT_TIMESTAMP)
            RETURNING run_id;
            """
        ),
        defaults
    )
    return result.scalar()


def create_test_lineage_factory(connection, run_id: int, **kwargs) -> None:
    """12 & 13. Parameterized Lineage Factory: Seeds a child record with customizable overrides [INDEX]."""
    defaults = {
        "target_table": "silver_measurements",
        "records_affected": 100
    }
    defaults.update(kwargs)
    defaults["run_id"] = run_id
    
    connection.execute(
        text(
            """
            INSERT INTO pipeline_lineage (run_id, target_table, records_affected, updated_at)
            VALUES (:run_id, :target_table, :records_affected, CURRENT_TIMESTAMP);
            """
        ),
        defaults
    )


# ==============================================================================
# 📋 15 & 16. NESTED FIXTURE LIFECYCLE DECK
# ==============================================================================

@pytest.fixture(scope="function")
def test_run(db_connection):
    """15. Run Fixture: Allocates runtime parent execution nodes on demand [INDEX]."""
    run_id = create_test_run_factory(db_connection)
    yield run_id
    
    # 17. Safe Teardown: Clears data upward from child rows to avoid foreign key violations [INDEX]
    with db_connection.begin() as txn:
        txn.execute(text("DELETE FROM event_processing WHERE event_id IN (SELECT event_id FROM pipeline_event_store WHERE run_id = :run_id);"), {"run_id": run_id})
        txn.execute(text("DELETE FROM pipeline_event_store WHERE run_id = :run_id;"), {"run_id": run_id})
        txn.execute(text("DELETE FROM pipeline_incidents WHERE run_id = :run_id;"), {"run_id": run_id})
        txn.execute(text("DELETE FROM pipeline_runs WHERE run_id = :run_id;"), {"run_id": run_id})


@pytest.fixture(scope="function")
def test_lineage(db_connection, test_run):
    """16. Nested Fixture: Automatically derives dependencies from parent to child [INDEX]."""
    create_test_lineage_factory(db_connection, test_run)
    yield test_run
    
    # 17. Safe Teardown: Clear the dependent child records first [INDEX]
    with db_connection.begin() as txn:
        txn.execute(text("DELETE FROM pipeline_lineage WHERE run_id = :run_id;"), {"run_id": test_run})
