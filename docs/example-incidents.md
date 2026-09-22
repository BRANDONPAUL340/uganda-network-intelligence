\# 📚 Production Incident Troubleshooting Guides



\---



\## 🟡 Scenario A — Gold Reporting Layer Stale (SEV2)

\### Symptoms

\* Visual Streamlit dashboard indicators remain unchanged across extraction cycles.

\* Freshness validation telemetry logs trigger active threshold breach warnings.



\### Step-by-Step Triage

1\. \*\*Audit `pipeline\_runs`:\*\* Check if the last ingestion run failed or threw a traceback error message.

2\. \*\*Audit Watermarks:\*\* Verify whether `processing\_watermarks` are updating or locked at an old index.

3\. \*\*Audit Container:\*\* Confirm that the PostgreSQL engine container has not run out of host storage space.



\### Resolution Response

Manually execute the incremental pipeline transformation module pass to force synchronization, then verify that high-watermarks update:

```cmd

python -m src.pipeline

python scripts/check\_watermarks.py

```



\---



\## 🔴 Scenario B — Operations Control Dashboard Unavailable (SEV1)

\### Symptoms

\* Browser routing to `http://localhost:8501` drops connections or returns a 500 error.



\### Step-by-Step Triage

1\. \*\*Audit Engine Process:\*\* Run `podman compose ps` to inspect active container health states.

2\. \*\*Audit Service Logs:\*\* Review output streams via `podman compose logs --tail=50 dashboard`.

3\. \*\*Audit Heartbeat Hook:\*\* Execute `podman compose exec dashboard python -m src.dashboard.healthcheck`.



\### Resolution Response

Force a restart of the frontend service node container to clear memory leaks or restart the network bridge socket:

```cmd

podman compose restart dashboard

```



