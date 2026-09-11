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
