\# 🛠️ Uganda Network Intelligence Incident Response Runbook



\## 🚦 System Triage Workflow



\### 1. Identify the Incident

Capture alerts from container log errors, unexpected user tickets, or direct dashboard telemetry anomalies \[INDEX].



\### 2. Determine Severity

Classify the failure into SEV1 through SEV4 buckets using your `incident-severity.md` ledger \[INDEX].



\### 3. Check PostgreSQL Storage Layer Stability

Verify that the data tier is up, accepting connections, and healthy \[INDEX]:

```cmd

podman compose ps

podman exec uganda\_network\_postgres18\_temp pg\_isready -U postgres -d network\_intelligence

```



\### 4. Audit Recent `pipeline\_runs` Logs

Query the core auditing ledger to catch execution failure status strings or runtime error logs \[INDEX]:

```cmd

python scripts/platform\_status.py

```



\### 5. Validate `processing\_watermarks` Freshness

Check whether incremental process tracking timestamps have stalled \[INDEX].



\### 6. Verify Dashboard Heartbeat Health

Execute the standalone application checker to isolate front-end server drop-offs \[INDEX]:

```cmd

podman compose exec dashboard python -m src.dashboard.healthcheck

```



\### 7. Audit Gold Tier Warehouses

Run ad-hoc row validations over reporting tables to isolate empty aggregations \[INDEX].



\### 8. Recover the Service Component

Apply targeted architectural remedies (e.g., restart docker-compose services, apply backward-compatible schema patches, or execute an image roll back) \[INDEX].



\### 9. Verify Post-Recovery State

Execute the end-to-end integration verification scripts to guarantee that data layers balance accurately \[INDEX].



\### 10. Document Post-Mortem Event

Log the root cause, exact resolution steps, and timeline metrics inside your deployment records to prevent recurrence \[INDEX].



