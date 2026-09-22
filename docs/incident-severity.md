\# 🚨 Incident Severity Classifications



\## 🔴 SEV1 — Critical (Platform Down)

\* \*\*Impact:\*\* Production infrastructure or visual control dashboards are completely unavailable \[INDEX].

\* \*\*Examples:\*\* PostgreSQL database container offline, Podman bridge network failure, or Streamlit app throwing a global 500 error \[INDEX].



\## 🟡 SEV2 — High (Core Processing Degraded)

\* \*\*Impact:\*\* The pipeline is active but fails to complete processing tiers, stalling incremental progress \[INDEX].

\* \*\*Examples:\*\* Ingestion runs crashing, data quality checks quarantining 100% of rows, or `processing\_watermarks` failing to update \[INDEX].



\## 🔵 SEV3 — Medium (SLA \& Minor Performance Degradation)

\* \*\*Impact:\*\* The platform remains functional, but runs fall outside performance thresholds or introduce low-risk data friction \[INDEX].

\* \*\*Examples:\*\* Transformation durations exceeding historical averages, localized data quality alerts, or processing lags \[INDEX].



\## 🟢 SEV4 — Low (Cosmetic \& Routine Maintenance)

\* \*\*Impact:\*\* Zero impact on processing paths or dashboard visibility \[INDEX].

\* \*\*Examples:\*\* Outdated documentation reference sheets, typos inside visual labels, or pending codebase version-tag bumps \[INDEX].



