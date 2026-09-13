# Database Sub-Platform

The Uganda Network & Service Intelligence Platform uses PostgreSQL as its primary data lakehouse engine and telemetry catalog backend [INDEX].

## 📋 Purpose

The database manages immutable raw operational data streams, enriched and standardized Silver records, optimized high-performance Gold analytical cubes, and isolated transaction-level operational metadata logs [INDEX].

## 🏗️ Structure

### 1. Source (Staging Layer)
* `sites`
* `equipment`
* `measurements`
* `incidents`

### 2. Silver (Standardization Layer)
* `silver_measurements`
* `silver_network_health`

### 3. Gold (Analytics Layer)
* `gold_site_daily_performance`
* `gold_equipment_health`

### 4. Pipeline Operations (Telemetry Ledgers)
* `pipeline_runs`
* `pipeline_stage_runs`
* `pipeline_lineage`
* `data_quality_results`

### 5. Views (Observability Layer)
* `pipeline_audit_report`
* `pipeline_operational_metrics`

## 🚀 Initialization & Deployment

To spin up a fresh replica data platform environment on a clean machine, initialize an empty PostgreSQL database named `network_intelligence` and execute this schema script file directly [INDEX]:

```bash
psql -U postgres -d network_intelligence -f database/schema.sql
```

The schema file builds every required database entity table, structural constraint check, optimization index tree, and query view required by the application.

## 🛡️ Reproducibility Guarantee

The structural blueprint is fully transaction-isolated and self-contained. It is designed to cleanly build the required data architecture on a completely empty PostgreSQL database instance without depending on any pre-populated tables [INDEX].

## 🔄 Database Migrations & Schema Versioning

Database migrations provide a versioned history of schema changes, ensuring that the database can evolve over time without data loss [INDEX].

Migration files are archived under:
`database/migrations/`

Files strictly follow a sequential numeric prefix naming convention:
`NNN_description.sql`

* `000_migration_tracking.sql` — Initializes the master version ledger.
* `001_initial_schema.sql` — Establishes the project structural baseline milestone [INDEX].
* `002_add_migration_checksum.sql` — Implements forward-only schema metadata extensions [INDEX].

### 🛠️ Execution Command
To manually run or synchronize the database migrations from the project root [INDEX]:
```bash
python -m src.migrations
```
The python migration engine checks the `schema_migrations` catalog table and only executes delta scripts that have not yet been recorded, ensuring absolute idempotency [INDEX].

### 📊 Audit Log Tracking
To query your structural evolution milestone log directly inside PostgreSQL [INDEX]:
```sql
SELECT version, description, applied_at
FROM schema_migrations
ORDER BY version;
```

### 🔒 Architectural Rules
Applied migration scripts are permanently immutable and must never be altered [INDEX]. Subsequent database alterations must be deployed via a newly numbered sequential migration script (e.g., `003_xxx.sql`) to maintain an uncorrupted audit trail [INDEX].
