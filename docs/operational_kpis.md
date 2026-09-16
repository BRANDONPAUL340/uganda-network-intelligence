# 🗺️ Operational KPI & Dashboard Data Layer

## 🎯 Purpose

The operational KPI layer provides stable, dashboard-ready database views for the Uganda Network & Service Intelligence data platform.

These views separate KPI calculation from downstream visualization tools and provide a consistent source of operational metrics.

---

## 📊 Pipeline KPIs

The `pipeline_kpis` view provides macro-level pipeline execution metrics.

Core metrics include:

* **Total Runs:** Total number of recorded pipeline executions.
* **Successful Runs:** Number of pipeline executions completed successfully.
* **Failed Runs:** Number of pipeline executions that failed.
* **Running Runs:** Number of pipeline executions currently recorded as running.
* **Pipeline Success Rate:** Percentage of recorded pipeline executions that completed successfully.

The primary database view is:

`pipeline_kpis`

---

## ❤️ Health KPIs

Health KPIs describe the operational state of the data platform and its pipeline execution environment.

The health layer tracks:

* Healthy checks
* Warning checks
* Critical checks
* Total health checks
* Daily health trends
* Current pipeline health

The main health views are:

`daily_pipeline_health`

`current_pipeline_health`

---

## 🚨 Alert KPIs

Alert KPIs provide visibility into operational conditions that require investigation.

The alert layer tracks:

* Critical alerts
* Warning alerts
* Alert counts
* Alert-producing health checks
* Operational conditions requiring attention

Alert information is derived from the platform's health and monitoring layer.

---

## 🔧 Stage KPIs

Stage KPIs provide granular visibility into individual pipeline processing stages.

The stage monitoring layer tracks:

* Stage executions
* Successful stage executions
* Failed stage executions
* Running stage executions
* Stage duration
* Records read
* Records inserted
* Records rejected
* Records skipped

The primary stage-level views are:

`pipeline_stage_kpis`

`pipeline_stage_summary`

---

## 🗄️ Operational Reporting Views

The platform exposes stable database reporting structures for downstream dashboards:

1. `pipeline_kpis` — macro-level pipeline execution metrics.
2. `pipeline_stage_kpis` — run-specific metrics for individual pipeline stages.
3. `pipeline_stage_summary` — aggregated stage performance and record-volume metrics.
4. `daily_pipeline_health` — historical health monitoring trends.
5. `current_pipeline_health` — current operational health snapshot.

---

## 🧠 Architecture Principle

Heavy KPI calculations should remain inside the data platform.

Downstream visualization tools such as Grafana, Power BI, Streamlit, or Apache Superset should consume these stable reporting views rather than independently recreating business logic.

This provides a consistent source of truth and keeps dashboard queries simple and predictable.

---

## 🔍 KPI Design Principle

Operational KPIs should be:

* **Measurable** — derived from recorded pipeline or monitoring data.
* **Repeatable** — calculated consistently across executions.
* **Traceable** — connected to underlying pipeline and stage records.
* **Dashboard-ready** — exposed through stable database views.
* **Operationally useful** — focused on execution, health, alerts, and stage performance.

---

## 📌 Required Operational Views

The operational KPI documentation corresponds to the following database objects:

* `pipeline_kpis`
* `pipeline_stage_kpis`
* `pipeline_stage_summary`
* `daily_pipeline_health`
* `current_pipeline_health`
