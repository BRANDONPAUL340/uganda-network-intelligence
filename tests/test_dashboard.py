"""
Uganda Network Intelligence Platform — Dashboard Analytics Integration Tests
Validates real-time aggregation metrics, edge cases, and fallback error paths [INDEX].
"""
import pytest
from sqlalchemy import text
from tests.factories import create_test_run_factory
from src.dashboard.monitoring import (
    get_pipeline_summary_metrics,
    get_recent_pipeline_logs,
    get_filtered_pipeline_runs,
    get_pipeline_run_steps_trace,
    get_data_quality_summary_metrics,
    get_filtered_data_quality_results,
    get_incidents_summary_metrics,
    get_filtered_incidents_logs,
    get_event_workers_summary_metrics,
    get_filtered_events_ledger,
    get_filtered_pipeline_lineage_logs,
)

from tests.factories import create_test_run_factory

@pytest.mark.integration
def test_get_pipeline_summary_metrics_handles_empty_database_gracefully(db_connection):
    """20 & 21. Empty State Test: Asserts that an empty database returns zeroed metric totals without crashing [INDEX]."""
    # Force clear baseline tracking metrics within the transaction rollback fence [INDEX]
    db_connection.execute(text("TRUNCATE TABLE pipeline_runs CASCADE;"))
    db_connection.execute(text("TRUNCATE TABLE pipeline_incidents CASCADE;"))
    
    metrics = get_pipeline_summary_metrics(connection=db_connection)
    
    assert metrics["status"] == "HEALTHY"
    assert metrics["total_runs"] == 0
    assert metrics["success_runs"] == 0
    assert metrics["failed_runs"] == 0
    assert metrics["open_incidents"] == 0


@pytest.mark.integration
def test_get_pipeline_summary_metrics_computes_correct_aggregates(db_connection):
    """20. Aggregation Test: Seeds explicit execution rows and asserts metric cards compute perfectly [INDEX]."""
    # Seed explicit test data using parameters [INDEX]
    create_test_run_factory(db_connection, status="SUCCESS", current_stage="BRONZE")
    create_test_run_factory(db_connection, status="SUCCESS", current_stage="GOLD")
    create_test_run_factory(db_connection, status="FAILED", current_stage="SILVER")
    
    metrics = get_pipeline_summary_metrics(connection=db_connection)
    
    assert metrics["status"] == "HEALTHY"
    assert metrics["total_runs"] >= 3
    assert metrics["success_runs"] >= 2
    assert metrics["failed_runs"] >= 1

# ==============================================================================
# 🔄 PIPELINE RUNS TRACE VALIDATION TIER (Day 223) [INDEX]
# ==============================================================================


@pytest.mark.integration
def test_get_filtered_pipeline_runs_isolates_status_criteria_precisely(db_connection):
    print(">>> TEST STARTED", flush=True)

    db_connection.execute(text("TRUNCATE TABLE pipeline_runs CASCADE;"))
    print(">>> TRUNCATE COMPLETE", flush=True)

    create_test_run_factory(db_connection, status="SUCCESS")
    print(">>> SUCCESS INSERT COMPLETE", flush=True)

    create_test_run_factory(db_connection, status="FAILED")
    print(">>> FAILED INSERT COMPLETE", flush=True)

    success_df = get_filtered_pipeline_runs(
        status_filter="SUCCESS",
        connection=db_connection,
    )
    print(">>> SUCCESS QUERY COMPLETE", flush=True)

    failed_df = get_filtered_pipeline_runs(
        status_filter="FAILED",
        connection=db_connection,
    )
    print(">>> FAILED QUERY COMPLETE", flush=True)

    assert not success_df.empty
    assert (success_df["status"] == "SUCCESS").all()

    assert not failed_df.empty
    assert (failed_df["status"] == "FAILED").all()


@pytest.mark.integration
def test_get_pipeline_run_steps_trace_returns_empty_on_unknown_identifier():
    """19. Edge Case Test: Asserts that querying an unknown run_id returns an empty frame without throwing crashes [INDEX]."""
    unknown_id = 89900234
    result_df = get_pipeline_run_steps_trace(run_id=unknown_id)
    assert result_df.empty
# ==============================================================================
# ✅ DATA QUALITY ENGINE TESTING TIER (Day 224) [INDEX]
# ==============================================================================


@pytest.mark.integration
def test_get_data_quality_summary_metrics_handles_empty_table_safely(db_connection):
    """Verifies that an empty data_quality_results catalog resolves to clean zeroed maps."""
    db_connection.execute(text("TRUNCATE TABLE data_quality_results CASCADE;"))

    metrics = get_data_quality_summary_metrics(connection=db_connection)

    assert metrics["status"] == "HEALTHY"
    assert metrics["pass"] == 0
    assert metrics["warn"] == 0
    assert metrics["fail"] == 0


@pytest.mark.integration
def test_get_filtered_data_quality_results_extracts_correct_row_properties(db_connection):
    """Asserts that quality filter queries fetch row attributes matching the physical schema."""
    db_connection.execute(text("TRUNCATE TABLE data_quality_results CASCADE;"))

    run_id = create_test_run_factory(
        db_connection,
        status="SUCCESS",
        current_stage="SILVER",
    )

    db_connection.execute(
        text(
            """
            INSERT INTO data_quality_results
            (
                run_id,
                table_name,
                check_name,
                check_type,
                status,
                records_checked,
                records_failed,
                failure_rate_pct,
                details,
                checked_at
            )
            VALUES
            (
                :run_id,
                'silver_measurements',
                'freshness_latency_check',
                'FRESHNESS',
                'FAIL',
                100,
                25,
                25.00,
                'Freshness exceeded threshold',
                CURRENT_TIMESTAMP
            );
            """
        ),
        {"run_id": run_id},
    )

    results = get_filtered_data_quality_results(
        status_filter="FAIL",
        connection=db_connection,
    )

    assert not results.empty
    assert results["check_name"].iloc[0] == "freshness_latency_check"
    assert results["status"].iloc[0] == "FAIL"
    
# ==============================================================================
# 🚨 OPERATIONAL INCIDENTS COCKPIT TESTING TIER (Day 225) [INDEX]
# ==============================================================================

@pytest.mark.integration
def test_get_incidents_summary_metrics_handles_empty_table_safely(db_connection):
    db_connection.execute(text("TRUNCATE TABLE incidents CASCADE;"))

    metrics = get_incidents_summary_metrics(connection=db_connection)
    assert metrics["total_incidents"] == 0
    assert metrics["open_incidents"] == 0
    assert metrics["resolved_incidents"] == 0
    assert metrics["critical_high_incidents"] == 0


@pytest.mark.integration
def test_get_filtered_incidents_logs_isolates_severities_precisely(db_connection):
    db_connection.execute(text("TRUNCATE TABLE incidents CASCADE;"))

    db_connection.execute(
        text(
            """
            INSERT INTO incidents
                (site_id, incident_type, severity, start_time, end_time, status, description)
            VALUES
                (1, 'Subnet Outage', 'CRITICAL', CURRENT_TIMESTAMP, NULL, 'OPEN',
                 'Core network block timed out.')
            """
        )
    )

    results = get_filtered_incidents_logs(
        severity_filter="CRITICAL",
        connection=db_connection,
    )
    assert not results.empty
    assert results["incident_type"].iloc[0] == "Subnet Outage"
    assert results["severity"].iloc[0] == "CRITICAL"

# ==============================================================================
# ⚡ ASYNCHRONOUS EVENT QUEUE TESTING TIER (Day 226) [INDEX]
# ==============================================================================

@pytest.mark.integration
def test_get_event_workers_summary_metrics_handles_empty_tables_gracefully(db_connection):
    """Verifies that empty messaging schemas resolve to clean zeroed structures without crashes [INDEX]."""
    db_connection.execute(text("TRUNCATE TABLE pipeline_event_store CASCADE;"))
    db_connection.execute(text("TRUNCATE TABLE event_processing CASCADE;"))
    
    metrics = get_event_workers_summary_metrics(
    connection=db_connection
)
    assert metrics["status"] == "HEALTHY"
    assert metrics["total"] == 0
    assert metrics["success"] == 0
    assert metrics["failed"] == 0
    assert metrics["retries"] == 0



@pytest.mark.integration
def test_get_filtered_events_ledger_assembles_relational_join_properties(
    db_connection,
):
    """Verify event records join correctly to processing status."""
    db_connection.execute(
        text("TRUNCATE TABLE pipeline_event_store CASCADE;")
    )
    db_connection.execute(
        text("TRUNCATE TABLE event_processing CASCADE;")
    )

    run_id = create_test_run_factory(
        db_connection,
        status="SUCCESS",
    )

    event_id = "00000000-0000-0000-0000-000000000226"

    db_connection.execute(
        text("""
            INSERT INTO pipeline_event_store
                (event_id, event_type, event_version, run_id,
                 event_time, producer, payload)
            VALUES
                (:event_id, 'QUALITY_CHECK_FAILED', '1.0',
                 :run_id, CURRENT_TIMESTAMP, 'test_engine', '{}');
        """),
        {
            "event_id": event_id,
            "run_id": run_id,
        },
    )

    results = get_filtered_events_ledger(
        type_filter="QUALITY_CHECK_FAILED",
        connection=db_connection,
    )

    assert not results.empty
    assert str(results["event_id"].iloc[0]) == event_id
    assert results["status"].iloc[0] == "PENDING"

# ==============================================================================
# 🔗 DATA LINEAGE COCKPIT MONITORING TESTS (Day 227) [INDEX]
# ==============================================================================

@pytest.mark.integration

def test_get_filtered_pipeline_lineage_logs_handles_empty_table_safely(
    db_connection,
):
    """Verify empty lineage results are handled safely."""
    db_connection.execute(
        text("TRUNCATE TABLE pipeline_lineage CASCADE;")
    )

    results = get_filtered_pipeline_lineage_logs(
        run_id_filter="All",
        connection=db_connection,
    )

    assert results.empty



@pytest.mark.integration
def test_get_filtered_pipeline_lineage_logs_completely_omits_operation_type_column(
    db_connection,
):
    """Verify lineage results match the physical database schema."""
    db_connection.execute(
        text("TRUNCATE TABLE pipeline_lineage CASCADE;")
    )

    run_id = create_test_run_factory(
        db_connection,
        status="SUCCESS",
    )

    db_connection.execute(
    text("""
        INSERT INTO pipeline_lineage
            (run_id, source_table, target_table,
             records_processed, created_at)
        VALUES
            (:run_id, 'bronze_measurements',
             'gold_site_daily_performance',
             5000, CURRENT_TIMESTAMP);
    """),
    {"run_id": run_id},
)
    results = get_filtered_pipeline_lineage_logs(
        run_id_filter="All",
        connection=db_connection,
    )

    assert not results.empty
    assert "operation_type" not in results.columns
    assert "target_table" in results.columns
    assert "gold_site_daily_performance" in results["target_table"].values