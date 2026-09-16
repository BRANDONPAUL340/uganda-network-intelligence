\# 🚀 Performance Engineering Logs



\## 📊 Day 91 Architectural Baseline



The project implements high-resolution PostgreSQL `EXPLAIN` and `EXPLAIN (ANALYZE, BUFFERS)` execution engines to measure query plan costs, memory batch parameters, and disk page cache interactions natively under rootless Podman \[INDEX].



\---



\## 🔍 Core Query Access Patterns



\### 🥈 Silver Layer Staging Tier

Common structural scan and filter pathways include:

\* \*\*Unique Key Lookups:\*\* `measurement\_id` targeted scans (leveraging implicit unique B-Tree primary constraints) \[INDEX].

\* \*\*Dimensional Slicing Grains:\*\* `site\_id` + `measured\_at` composite queries (leveraged by incremental promotional logic steps) \[INDEX].

\* \*\*Incremental Perimeter Boundary Queries:\*\* `raw\_measurement\_id` relative sweeps to process fresh raw files \[INDEX].



\### 🥇 Gold Layer Aggregation Tier

Common analytical calculation blocks include:

\* \*\*Composite Uniqueness Fences:\*\* `site\_id` + `measurement\_date` duplicate isolation \[INDEX].

\* \*\*Daily Dimensional Rollups:\*\* Multi-attribute group rollups executing table joins between staging and dimension tables (`silver\_measurements` ⨝ `sites`) \[INDEX].



\---



\## 🛠️ Materialized Index Directory



\### Newly Deployed Performance Additions

\* \*\*`idx\_silver\_site\_date`\*\*: An optimized composite B-Tree index built on `silver\_measurements(site\_id, measured\_at)`. This index speeds up incremental slicing lookups and protects your daily query paths \[INDEX].



\### Reused Infrastructural Assets

Implicit unique primary indexes (`raw\_measurements\_pkey`, `silver\_measurements\_pkey`) are fully shared and utilized across all extraction sweeps to save database processing power \[INDEX].



\---



\## 🧠 Core Engineering Principles Learned



1\. \*\*Measure First, Deploy Second:\*\* Indices are costly structures that add to disk storage and slow down write operations (`INSERT` / `UPDATE`) \[INDEX]. Only build an index if you can back it up with raw execution metrics from real query patterns \[INDEX].

2\. \*\*Planner Math Safety Gates:\*\* Just because an index is live on disk does not mean the query planner will use it. For small datasets that fit into a single cache block (`shared hit=1`), PostgreSQL will choose a sequential scan (`Seq Scan`) because reading the pages directly is significantly cheaper than traversing an index tree \[INDEX].



