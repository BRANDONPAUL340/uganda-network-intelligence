\# 🚀 Release Process \& Deployment Readiness



\## 🎯 Purpose

This document establishes the official release guidelines for the Uganda Network \& Service Intelligence data platform \[INDEX]. Following these steps prevents bad code, broken metrics, or untested schema changes from reaching production \[INDEX].



\---



\## 🚦 The 10-Step Release Lifecycle Workflow



\### 1. Develop \& Isolate

All feature additions, pipeline stages, or visual components are developed within dedicated feature branches \[INDEX].



\### 2. Test Locally

Run ad-hoc functionality checks on your local workstation before staging changes \[INDEX].



\### 3. Run Pytest Suite

Execute the entire local validation suite to ensure your code configurations remain completely stable:

```cmd

set DATABASE\_URL=postgresql+psycopg://postgres:postgres@localhost:5433/network\_intelligence

pytest -v

```



\### 4. Validate Idempotent Migrations

Verify that your database migration runner runs cleanly without breaking existing schemas on disk \[INDEX]:

```cmd

python -m src.migrations

```



\### 5. Validate Podman Compose Sockets

Audit your multi-container orchestration manifests to confirm YAML compatibility \[INDEX]:

```cmd

podman compose config

```



\### 6. Build the Standalone OCI Container Images

Compile your production-grade application and dashboard service container layers \[INDEX]:

```cmd

podman compose build

```



\### 7. Run Dashboard Application Health Checks

Verify that the frontend container can successfully reach your container database over the private network mesh \[INDEX]:

```cmd

podman compose exec dashboard python -c "from src.dashboard.health import get\_dashboard\_health; print(get\_dashboard\_health())"

```



\### 8. Push Code Changes to GitHub

Commit your changes and stream your codebase live onto your public version control ledger \[INDEX].



\### 9. GitHub Actions Validation Passes

GitHub Actions hooks onto your fresh push, spins up a runner environment, and validates the entire platform \[INDEX].



\### 10. Tag the SemVer Release

Once your continuous integration workflow turns green, tag your stable commit build on GitHub using Semantic Versioning rules \[INDEX]:

```cmd

git tag -a v1.0.0 -m "Official Production Stability Release Version 1.0.0"

git push origin v1.0.0

```



\---



\## 🧠 Core Operational Principle

\*\*Never create a release from code that has not passed CI.\*\* The remote automation runner serves as the final quality gate to guarantee platform stability \[INDEX].



