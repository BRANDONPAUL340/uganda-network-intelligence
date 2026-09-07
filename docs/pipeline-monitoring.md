# Pipeline Monitoring

## Pipeline Run Summary

The `pipeline_run_summary` database view provides a consolidated, high-performance operational view of pipeline executions. It abstractly unifies data from macro runtime logs, micro stage performance states, and data quality check scorecards.

## Exposed Metrics Ledger

The view exposes these core analytics metrics:
* **`run_id`**: Auto-incremented execution transaction sequence index key.
* **`pipeline_name`**: The registered unique platform system identity key string.
* **`started_at` / `completed_at`**: Precise chronological transaction timestamps.
* **`current_stage`**: High-precision progress string marker showing current or termination states.
* **`status`**: Overall pipeline closeout condition flag (`SUCCESS` or `FAILED`).
* **`records_processed`**: Volume of records newly processed/inserted during this specific pipeline run delta.
* **`duration_seconds`**: High-resolution runtime elapsed time calculated at millisecond scales.
* **`quality_checks`**: The total count of data contract and boundary rules evaluated.
* **`quality_passed` / `quality_failed`**: Volumetric check pass and failure counts.
* **`failed_records`**: Absolute count of data row items violating validation contract boundary limits.
* **`failed_table` / `failed_check`**: Direct context fields flagging the specific anomaly origin points.
* **`pipeline_health`**: Derived conditional operating health state classification indicator string.

## Pipeline Health Classifications

### `HEALTHY`
The data pipeline completed successfully, and 100% of all integrated data contract validation rules passed perfectly.

### `WARNING`
The pipeline completed its execution lifecycle, but one or more data quality check rules reported failures that require operator attention.

### `FAILED`
The baseline execution pipeline itself crashed, or a non-negotiable critical gate circuit breaker aborted the process to protect target analytical layers.

## Operational Query Example

```sql
SELECT
    run_id,
    status,
    pipeline_health,
    records_processed,
    duration_seconds,
    quality_checks,
    quality_passed,
    quality_failed
FROM pipeline_run_summary
ORDER BY run_id DESC;
```
