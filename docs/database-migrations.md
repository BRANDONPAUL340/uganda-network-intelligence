# Database Migrations Control Layer

The Uganda Network & Service Intelligence Platform manages all database schema modifications as a series of version-controlled, declarative SQL scripts stored inside the `migrations/` directory.

## Sequential Migration Order

Migrations are strictly numbered and must be executed in chronological order:

```text
001_initial_schema.sql         ──► Foundational data layer tables and core registers
002_pipeline_observability.sql  ──► Telemetry indicators and high-resolution profiling columns
003_pipeline_summary.sql        ──► Unified multi-table performance views and scorecard health calculations
```

## Architectural Purpose

Migrations turn database infrastructure into **reproducible, declarative code**. Instead of relying on manual, undocumented SQL mutations executed via the terminal, the platform tracks database changes under version control alongside application source files.

## Core Architectural Separation of Concerns

* **Schema Migrations (Structure):** Define the structural data constraints and blueprints (`CREATE`, `ALTER`, `DROP`).
* **Data Pipelines (Execution):** Responsible for loading, mutating, and transforming rows inside those structures (`INSERT`, `UPDATE`).

## Framework Implementation Status

The database migration layer is being introduced incrementally. The next major sprint target is to extend our initial schema contracts to include all intermediate Silver layer tables, Gold reporting aggregates, and automated data quality registries inside the main migration ledger.
