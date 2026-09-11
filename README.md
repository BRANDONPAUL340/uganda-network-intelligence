# Uganda Network & Service Intelligence Platform

A production-oriented data engineering pipeline for transforming telecommunications network measurements into reliable operational and analytical insights.

---

## 📋 Overview

The Uganda Network & Service Intelligence Platform is an end-to-end data engineering project designed to process telecommunications network data and transform operational measurements into analytics-ready datasets. 

The platform focuses on data quality, reliable transformations, pipeline observability, data lineage, operational monitoring, and reproducible execution.

---

## 🎯 Problem Statement

Telecommunications network operations generate massive streams of raw measurements such as:
* **Traffic Volume**: Hourly cellular data transmission counters (MB).
* **Latency & Packet Loss**: Microsecond connection delay tracking and transmission drop rates.
* **Signal Strength & Availability**: Physical RF power metrics (dBm) and overall cell site uptime percentages.
* **Asset Tracking & Incidents**: Hardware manufacturing specifications matched to live operational network outages.

Raw operational data is not immediately suitable for reliable analysis. It frequently suffers from schema drift, missing fields, orphaned hardware keys, or structural type mutations. The platform therefore provides a structured, production-ready pipeline that validates source data, transforms it through quality and analytical layers, tracks pipeline execution, and exposes operational metrics for monitoring.

---

## 🏗️ Architecture

The platform follows a decoupled, multi-tier data engine layer layout:

```text
                             PostgreSQL Source Tier
                         ┌─────────────┼─────────────┐
                         ▼             ▼             ▼
                       sites       equipment    measurements
                         │             │             │
                         └─────────────┼─────────────┘
                                       │
                                       ▼
                                ┌─────────────┐
                                │   QUALITY   │
                                │             │
                                │ Schema      │
                                │ validation  │
                                │ Data checks │
                                └──────┬──────┘
                                       │
                                       ▼
                                ┌─────────────┐
                                │   SILVER    │
                                │             │
                                │ Cleaned     │
                                │ measurements│
                                │ Network     │
                                │ health      │
                                └──────┬──────┘
                                       │
                                       ▼
                                ┌─────────────┐
                                │    GOLD     │
                                │             │
                                │ Site daily  │
                                │ performance │
                                │ Equipment   │
                                │ health      │
                                └─────────────┘
```

### Operational Metadata Architecture
Pipeline execution state tracking is completely decoupled from analytical data layers, establishing an independent audit trail:

```text
pipeline_runs (Macro Monitoring Ledger)
      │
      ▼
pipeline_stage_runs (Micro Processing Phases)
      │
      ▼
pipeline_lineage (Asset Traceability Loops)
      │
      ├── source_table
      └── target_table
```

Additional monitoring layers:
* `pipeline_audit_report`: Consolidated view layer combining runs, timers, and lineages.
* `pipeline_operational_metrics`: Diagnostic SLA duration and freshness scorecard view.
* `logs/pipeline.log`: Persistent file logging tracking runtime thread stacks.

---

## 📊 Data Layers

### 1. Source Layer (Staging)
Contains raw, immutable source tables direct from edge collectors:
* `sites`: Cellular tower geographical lookup maps.
* `equipment`: Active hardware tracking registers (RAN models, manufacturers).
* `measurements`: Raw telemetry parameter counters.
* `incidents`: Real-time network fault tickets.

### 2. Quality Layer (Firewall Gate)
Acts as a structural circuit breaker before transformations run, validating:
* Required tables exist on disk.
* Required columns are present.
* Columns match expected structural data types (`bigint`, `numeric`).
* Reference integrity and duplicate records are audited.

### 3. Silver Layer (Standardization)
Holds cleaned, enriched, and classified operational data tracking items:
* `silver_measurements`: Wide denormalized fact records mapped to site metadata.
* `silver_network_health`: Granular performance tracking indices classification (`Healthy`, `Warning`, `Critical`) driven by dynamic configuration variables.

### 4. Gold Layer (Analytics Cubes)
Holds highly optimized, aggregate metrics cubes tailored for downstream business applications:
* `gold_site_daily_performance`: Pre-computed site-level latency and traffic averages.
* `gold_equipment_health`: Aggregated hardware component health tracking matrices.

---

## 🎛️ Network Health Classification

Network health is classified dynamically using configurable operational thresholds. This decouples business logic from core execution code, allowing modifications without software redeployment.

### Critical
A measurement is classified as **Critical** when:
* Availability drops below the critical availability threshold.
* **OR** packet loss exceeds the critical packet-loss threshold.
* **OR** latency exceeds the critical latency threshold.

### Warning
A measurement is classified as **Warning** when it does not trigger a Critical flag but violates a warning threshold on any of the core connection parameters.

### Healthy
A measurement is classified as **Healthy** when all configured warning and critical constraints are fully satisfied.

---

## 🔄 Pipeline Execution Flow

The master orchestrator strictly executes stages in an isolated lifecycle sequence:

1. **Start pipeline run**: Provisions a tracking run entry inside `pipeline_runs`.
2. **Validate source schema**: Runs pre-flight structural contracts checking.
3. **Run data-quality checks**: Launches 18-point core logical integrity audits.
4. **Transform source data into Silver**: Executes denormalization and health classifications.
5. **Transform Silver data into Gold**: Refreshes reporting summary data cubes.
6. **Record stage metrics**: Logs timers and status values per phase into `pipeline_stage_runs`.
7. **Record data lineage**: Logs target dependencies to `pipeline_lineage`.
8. **Evaluate pipeline operational metrics**: Calculates duration and freshness SLAs.
9. **Mark the pipeline run as successful or failed**: Saves proper transactional closeout exit states to disk.

Pipeline failures are captured securely in pipeline metadata tables and application log files.

---

## 🛡️ Idempotency & Rerun Safeguards

The transformation pipeline is designed to support safe repeated execution.

Silver measurement loading uses the unique measurement identifier as a conflict resolution key (`ON CONFLICT (measurement_id) DO NOTHING`) so that previously processed measurements are not duplicated on disk.

This allows the pipeline to be rerun without creating duplicate Silver records when the source staging data has not changed. Repeated execution is fully tested as a core part of the platform's production validation process.

---

## 🩺 Data Quality

The platform performs multiple categories of data-quality validation to protect downstream analytic models.

### Structural validation
Checks that required tables and columns exist and that important columns use expected database types (`bigint`, `numeric`).

### Referential integrity
Validates relationships between incoming metrics and structural lookups:
* `measurements` to `sites`
* `measurements` to `equipment`

### Duplicate detection
Checks for duplicate logical records in important source and transformed datasets to ensure transaction accuracy.

### Range validation
Enforces physical boundaries on connection parameters:
* `traffic_mb` >= 0
* `latency_ms` >= 0
* `packet_loss_pct` between 0 and 100
* `availability_pct` between 0 and 100

### Severity
Quality failures are classified cleanly as `INFO`, `WARNING`, or `CRITICAL`. Critical quality failures can affect overall pipeline health.

---

## 👁️ Observability

Pipeline execution is fully observable through several integrated monitoring mechanisms.

### Application logging
Pipeline events are written directly to `logs/pipeline.log`. Logs capture microsecond-accurate stage milestones, durations, row-accounting statistics, and structural failures.

### Pipeline tracking
The `pipeline_runs` table records overall execution stats. The `pipeline_stage_runs` table isolates the execution of individual phases.

### Lineage
The `pipeline_lineage` table tracks source-to-target dataset relationships.

### Audit reporting
The `pipeline_audit_report` view combines execution, stage, and lineage information into a single interface for fast operational investigation.

### Operational metrics
The `pipeline_operational_metrics` view exposes pipeline duration, SLA status, latest measurement dates, data freshness intervals, and freshness SLA metrics.

---

## 🚀 Current Capabilities

- **PostgreSQL-backed data model**: Transactional relational repository mapping telecom metrics securely.
- **Layered data architecture**: Clear isolation boundaries applied via Medallion staging, Silver, and Gold tiers.
- **Data-quality validation**: Robust 18-point data quality gates tracking logical record parameters.
