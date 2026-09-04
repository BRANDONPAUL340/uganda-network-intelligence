from src.monitoring import PipelineMetrics  # ◄ Will resolve cleanly via __init__.py now!

def test_pipeline_metrics_calculation():
    metrics = PipelineMetrics(
        records_read=100,
        records_inserted=80,
        records_rejected=10,
        records_skipped=10,
    )
    assert metrics.records_processed == 90


def test_pipeline_metrics_summary_serialization():
    """
    ARRANGE, ACT & ASSERT: Verifies that our summary dictionary serialization 
    extracts all multi-tier performance parameters with absolute precision.
    """
    metrics = PipelineMetrics(
        records_read=100,
        records_inserted=80,
        records_rejected=10,
        records_skipped=10,
    )

    summary = metrics.summary()

    assert summary["records_read"] == 100
    assert summary["records_inserted"] == 80
    assert summary["records_rejected"] == 10
    assert summary["records_skipped"] == 10
    assert summary["records_processed"] == 90
