# Pipeline Observability & Telemetry

The Uganda Network & Service Intelligence Platform records high-fidelity operational metrics directly inside your database engine for every execution pass.

## Captured Core Metrics

* **`records_read`**: Genuinely new or duplicate records examined from the raw source file.
* **`records_inserted`**: Fresh delta records successfully written to your staging tables.
* **`records_rejected`**: Anomalous records caught and routed straight into quarantine.
* **`records_skipped`**: Duplicate historical records skipped by our O(1) memory filters.
* **`records_processed`**: Active table mutations (**`records_inserted`** + **`records_rejected`**).
* **`duration_seconds`**: Precision runtime calculated natively by PostgreSQL interval arithmetic.

## Structural Execution Statuses

* **`RUNNING`**: The processing loop is currently active and transforming files.
* **`SUCCESS`**: The pipeline completed all Medallion processing stages without any errors.
* **`FAILED`**: A data contract violation or a system crash tripped an immediate circuit breaker.

## High-Value Operational Inquiries

The database historical tracking ledger allows you to answer these production queries using standard SQL:
1. When did the pipeline last run and was it successful?
2. How many records were skipped or quarantined due to quality bugs?
3. How long did the job take, and what is our overall systemic processing velocity?
4. Which historical execution runs were the slowest?

## Data Ops Design Principle

Pipeline execution metrics should be fully observable and transparent without requiring heavy business intelligence dashboard tools. Storing operational history directly in the relational ledger ensures that engineers can use plain SQL to investigate data velocity and system performance issues instantly.
