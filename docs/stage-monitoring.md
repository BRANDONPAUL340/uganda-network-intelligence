# Stage-Level Pipeline Monitoring

The Uganda Network & Service Intelligence Platform logs granular execution metrics for individual transformation and processing layers.

## Tracked Stages

* **`INGESTION`**: Boundary file parser and data contract enforcement firewall gateway.
* **`SILVER`**: Clean data enrichment tier, hardware schema matching, and network health profiling.
* **`GOLD`**: Analytical slice materialization and partition-aware upsert loops.

## Granular Stage Metrics

Every execution block writes these metrics natively into the database:
* **Start and Completion Timestamps**: Absolute historical chronology markers.
* **Execution Status**: Discrete operational flags (`RUNNING`, `SUCCESS`, `FAILED`).
* **Volumetric Sub-Counters**: Granular indicators for rows read, inserted, rejected, and skipped.
* **Duration Seconds**: High-precision delta runtimes calculated natively by PostgreSQL.
* **Error Message**: Explicit exception traces if a processing failure trips the circuit breaker.

## Why This Matters

* **Macro vs. Micro Visibility**: Pipeline-level metrics tell us if the overall job finished. Stage-level profiling tells us exactly *which step* failed or caused a bottleneck.
* **Efficiency Analysis**: Quantifies the exact ratio of data read to written across every layer of the Medallion architecture.
* **Reliability Metrics**: Tracks historical failure frequencies to isolate brittle infrastructure links.

## Core Operational Principle

A production data pipeline must provide enough structured metadata to isolate bugs, diagnose system failures, and profile performance variables without requiring engineers to parse loose text files or application logs manually.
