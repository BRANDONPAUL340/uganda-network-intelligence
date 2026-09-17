\# 📊 Dashboard Observability Architecture



\## 🎯 Purpose

The Uganda Network \& Service Intelligence dashboard features application-level observability to trace database connectivity, measure query performance parameters, and capture operational errors gracefully \[INDEX].



\---



\## 🚦 Health Monitoring Safety Gates

The dashboard monitors PostgreSQL connectivity by running a lightweight `SELECT 1` heartbeat query before attempting to pull metric data panels \[INDEX]. This prevents broken interface states and provides actionable error notifications if a connection drops \[INDEX].



\---



\## ⏱️ High-Resolution Query Telemetry Logging

Every reporting data request executed by the data-access layer captures and logs \[INDEX]:

\* \*\*Query Name:\*\* Unique identifier string to flag the target view \[INDEX].

\* \*\*Execution Duration:\*\* High-resolution stopwatch timing tracking query speeds \[INDEX].

\* \*\*Rows Returned:\*\* Total dataset records fetched \[INDEX].

\* \*\*Failures and Exceptions:\*\* Full Python stack traces captured automatically by the logger if a request fails \[INDEX].



\---



\## 🔧 Embedded Frontend Diagnostics

The dashboard provides a dedicated diagnostics panel for maintenance and troubleshooting \[INDEX]:

\* \*\*Application Version:\*\* Hardcoded build tracking using standard semantic version tags \[INDEX].

\* \*\*Database Status:\*\* Active indicator displaying connection state metadata \[INDEX].

\* \*\*Dashboard Timestamp:\*\* Persistent UTC clock marking exactly when the UI was rendered \[INDEX].

\* \*\*Active Database Queries:\*\* Live view tracking active, running SQL requests straight out of `pg\_stat\_activity` \[INDEX].



\---



\## 🐋 Containerized Service Infrastructure

The dashboard runs as a separate, unprivileged service tier isolated from the backend database container using Podman.

Operational commands include:

- `podman compose ps` (Check container health status)
- `podman compose logs dashboard` (Review streaming telemetry log output)
\---



\## 🧠 Core Architecture Boundary Rules

```text

&#x20; PostgreSQL 18 ──► Reporting Views ──► Dashboard Data Layer ──► Streamlit Engine ──► User Browser

```

The frontend dashboard acts strictly as a \*\*presentation and observability layer\*\* \[INDEX]. All data quality sorting, aggregation equations, and metric thresholds are calculated inside your database views, ensuring a single source of truth across all tools \[INDEX].



