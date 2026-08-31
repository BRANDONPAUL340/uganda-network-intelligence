# Uganda Network & Service Intelligence Platform

A production-grade data engineering project designed to orchestrate and analyze network infrastructure, equipment component health, service performance metrics, and tower network incidents in Uganda.

## 🏛️ Platform Architecture

```text
       Incoming Raw Staging Area (PostgreSQL)
                        │
                        ▼
             ┌─────────────────────┐
             │  Data Quality Gate  │ ─── (Rejects bad logic / impossible records)
             └──────────┬──────────┘
                        │
                  (Clean Records)
                        ▼
             ┌─────────────────────┐
             │    Silver Layer     │ ─── (Enriches models / tracks ingestion deltas)
             └──────────┬──────────┘
                        │
             ┌─────────────────────┐
             │     Gold Layer      │ ─── (Computes daily BI dashboard aggregates)
             └─────────────────────┘
```

## 🛠️ Technology Stack

- **Core Orchestrator:** Python 3 (Modular Pipeline Application)
- **Relational Storage Engine:** PostgreSQL (Enterprise Relational DB Cluster)
- **Object-Relational Mapping (ORM):** SQLAlchemy 2.0 & `psycopg` (v3 Binary Driver Layer)
- **Data Querying Core:** Advanced SQL Aggregates, Check Constraints, & Transaction Controls
- **Version Control System:** Git & GitHub Architecture Profiles

## 📊 Medallion Architecture Data Layers

### 🟫 Raw Staging Area
Captures raw operational network logs, hardware specifications, and tracking telemetry packets arriving directly from field monitoring equipment.

### 🥈 Silver Transform Tier
Validates data through an explicit quality gateway firewall. Clean records undergo incremental schema parsing and join processing using performance index lookups (`ON CONFLICT DO NOTHING`) to completely eliminate duplication compute cycles.

### 🥇 Gold Aggregation Layer
Calculates non-destructive, business-ready aggregates, such as regional tower daily totals and long-term equipment availability averages, without deleting structural definitions from disk.

## ⚙️ Advanced Pipeline Engine Features

- **Incremental Processing Delta Loops:** Only transforms net-new data updates, saving valuable server compute time.
- **Data Quality Firewall Gate:** Aborts automated jobs instantly if corrupted field metrics are detected.
- **Comprehensive Run Observability:** Tracks execution durations down to the millisecond using `time.perf_counter()`.
- **System Diary Audit Ledger:** Registers pipeline health statuses (`STARTED`, `SUCCESS`, `FAILED`) to internal table archives dynamically.
- **Decoupled Configuration State Matrix:** Protects local passwords by isolating variable credentials to hidden environment arrays (`.env` -> `config.py`).
## 🔄 End-to-End Pipeline Execution

The platform processes network monitoring telemetry through a fully automated, synchronized end-to-end data pipeline:

1. **Bronze CSV Ingestion:** Extracts raw, flat-file network telemetry packets from our landing archive zone.
2. **Record Validation Gateway:** Filters records in memory to catch missing required fields or logical range errors before calling database connections.
3. **Idempotent Loading:** Securely streams validated records down to our raw PostgreSQL staging tables.
4. **Data Quality Gateway Firewall:** Automatically audits database-wide stability constraints before transforming data layers.
5. **Silver Layer Transformation:** Enriches raw facts with relational metadata models and filters out duplicate rows incrementally.
6. **Gold Analytics Tier:** Truncates and refreshes high-level business intelligence aggregates for daily reporting layers.
7. **Pipeline Run Auditing:** Logs microsecond runtime speeds, error trace records, and volumetric data balances down to a central tracking ledger table.

The ingestion framework is designed to be completely **idempotent**, using a natural composite business key combination (**`equipment_id` + `measured_at`**) as a uniqueness firewall to confidently block duplicate measurements without throwing platform errors or corrupting your analytical trends.
