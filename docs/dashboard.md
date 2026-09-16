# 📊 Operations Dashboard Architecture

## 🎯 System Overview

The Uganda Network & Service Intelligence dashboard provides a visual operational interface built on top of PostgreSQL reporting views.

The dashboard is designed for monitoring pipeline execution, system health, operational KPIs, stage performance, and network site performance.

---

## 🛠️ Technology Stack

* **Language:** Python 3.14
* **Frontend UI Framework:** Streamlit
* **Interactive Charting:** Plotly Express
* **Database:** PostgreSQL 18
* **Container Runtime:** Podman
* **Database Access:** SQLAlchemy + Psycopg 3
* **Data Processing:** Pandas

---

## 🔀 Unified Linear Data Flow

```text
Network Sources
      │
      ▼
RAW Ingestion
      │
      ▼
Quality Filter
      │
      ▼
Silver Staging
      │
      ▼
Gold Analytics
      │
      ▼
PostgreSQL Reporting Views
      │
      ▼
Streamlit Dashboard
```

The Streamlit layer consumes prepared reporting views rather than duplicating transformation or KPI logic.

---

## 📊 Operational KPIs

The dashboard exposes operational KPIs calculated by the PostgreSQL reporting layer.

Primary KPI sources include:

* `pipeline_kpis`
* `pipeline_stage_kpis`
* `pipeline_stage_summary`
* `daily_pipeline_health`
* `current_pipeline_health`

Operational KPIs include:

* Total pipeline runs
* Pipeline success rate
* Pipeline failures
* Current system health
* Historical health percentage
* Active alerts
* Critical alerts
* Stage execution counts
* Stage success rates
* Stage processing duration
* Records read
* Records inserted
* Records rejected
* Records skipped

---

## 🟢 Current Pipeline Health

The dashboard displays the latest overall platform health state.

Possible operational states include:

* **HEALTHY**
* **WARNING**
* **CRITICAL**
* **UNKNOWN**

The dashboard presents the current state and the associated health-check timestamp.

---

## 📈 Daily Pipeline Health Timeline

The dashboard provides an interactive timeline based on `daily_pipeline_health`.

The timeline can be used to observe:

* Historical health percentage
* Changes in platform availability
* Warning and critical periods
* Operational trends over time

---

## ⚙️ Pipeline Stage Performance

The stage-performance section consumes `pipeline_stage_summary`.

It provides visibility into:

* Stage execution counts
* Successful executions
* Failed executions
* Success rate
* Average execution duration
* Records read
* Records inserted
* Records rejected
* Records skipped

This provides an operational view of individual pipeline processing stages.

---

## 📡 Network Site Performance

The dashboard can expose Gold-layer network performance information for individual sites.

This allows operators to inspect analytical metrics at site level without requiring the dashboard to perform the underlying aggregation itself.

---

## 🏗️ Dashboard Architecture Principle

The dashboard is a **presentation layer**, not the primary business-logic layer.

The architecture follows:

**PostgreSQL → Reporting Views → Streamlit**

PostgreSQL performs the core aggregation and KPI calculations.

Streamlit is responsible primarily for:

* Displaying metrics
* Rendering tables
* Rendering charts
* Presenting health states
* Providing an operator-friendly interface

This separation keeps the frontend lightweight and makes the reporting layer reusable by other visualization tools.

---

## 🔒 Database Access

The dashboard obtains its database connection through the project's centralized database configuration.

It does not contain hard-coded production credentials.

Reporting views are explicitly controlled by the dashboard so that arbitrary database objects are not requested dynamically.

---

## 🚀 Operational Usage

Start the dashboard from the project root with:

```text
python -m streamlit run src/monitoring/dashboard.py
```

The dashboard should connect to the configured PostgreSQL instance and retrieve metrics from the reporting views.

---

## 🧪 Validation

Dashboard documentation is validated automatically through the project's test suite.

The documentation test verifies that this architecture guide exists and contains the core technology and KPI concepts required by the project.

The dashboard Python module should also pass compilation before deployment:

```text
python -m py_compile src/monitoring/dashboard.py
```
