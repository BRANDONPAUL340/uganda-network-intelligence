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
