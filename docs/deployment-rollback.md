\# 🔄 Production Deployment Rollback Runbook



\## 🎯 Purpose

This operational protocol outlines the instructions to reverse a failed application release and instantly recover a stable platform state \[INDEX].



\## 🚦 Incident Recovery Sequence

```text

&#x20; Incident Detected ──► Stop Deployment ──► Modify Compose Tag ──► Relaunch Stack ──► Run verification script

```



\## 🛠️ Step-by-Step Rollback Execution

If monitoring alerts trigger or the deployment verifier returns a non-zero exit code (`1`) after an infrastructure change \[INDEX]:



1\. Open your production manifest file: `docker-compose.prod.yml` \[INDEX].

2\. Identify the broken `image:` tag under the `dashboard` service definition node \[INDEX].

3\. Modify the version back to the previous \*\*known-good, verified release artifact\*\* (e.g., changing from `1.0.1` back to `1.0.0`) \[INDEX]:

&#x20;  ```yaml

&#x20;  image: ghcr.io/brandonpaul340/uganda-network-dashboard:1.0.0

&#x20;  ```

4\. Re-trigger the container runtime engine to pull and deploy the old immutable binary image layers instantly \[INDEX]:

&#x20;  ```cmd

&#x20;  podman compose -f docker-compose.prod.yml up -d

&#x20;  ```

5\. Re-run the verification script inside the container to certify recovery success \[INDEX]:

&#x20;  ```cmd

&#x20;  podman compose -f docker-compose.prod.yml exec dashboard python scripts/verify\_deployment.py

&#x20;  ```



