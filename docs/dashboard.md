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

---

## 🎛️ Multidimensional Interactive Filters
The operations cockpit implements an advanced cascading filter mechanism [INDEX]:
* **Geographical Region Slicing:** Dynamically isolates regional data blocks [INDEX].
* **Cascading District Slicing:** Automatically filters district dropdown choices based on the selected region [INDEX].
* **Timeline Date Range Picker:** Slices out custom chronological windows using secure named SQL parameters [INDEX].
* **Granular Site Drill-Down:** Allows operators to filter down and view daily performance logs for individual cell towers [INDEX].

## 📊 Executive Network Performance KPIs
The summary matrix layer computes six central performance indicators using a single database calculation loop [INDEX]:
* **Active Monitored Sites:** Distinct count of active cellular tower locations [INDEX].
* **Total Measurements:** Cumulative count of successfully ingested telemetry records [INDEX].
* **Average Network Traffic (MB):** Data volume trends across selected boundaries [INDEX].
* **Average Latency (ms):** Raw round-trip response timing tracking SLA limits [INDEX].
* **Average Network Packet Loss (%):** Core network quality metrics [INDEX].
* **Core Network Availability (%):** Platform availability percentage calculation [INDEX].

## 📈 Rich Visualizations & Chart Controls
The presentation layer implements interactive Plotly charts to expose trends [INDEX]:
* **Horizontal Site Availability Bar Chart:** Quickly isolates which specific towers have lower availability [INDEX].
* **Vertical Latency Analyzer Bar Chart:** Instantly tracks latency variations across different tower locations [INDEX].
* **Network Traffic Line Chart:** Plots data volume changes over time to monitor bandwidth trends [INDEX].
* **Pipeline Health State Distribution Pie Chart:** Summarizes pipeline status categories across your history log [INDEX].
* **Platform Availability Timeline Line Graph:** Tracks long-term platform stability over time [INDEX].

## 🧠 Core Data Architecture Boundary Rules
**The dashboard remains a presentation layer.** All business rules, threshold calculations, data quality filters, and aggregation logic remain in the PostgreSQL reporting views. The frontend dashboard focuses exclusively on visualization, while your containerized database tier handles all data crunching [INDEX].

```
