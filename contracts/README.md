# Data Contracts Registry

The Uganda Network & Service Intelligence Platform uses declarative, versioned data contracts to govern data structures, semantic meanings, and boundary expectations across all platform components.

## Active Schema Blueprints

| Dataset Module | Configuration Registry Mapping Asset | Current Production Version | Classification Type |
| :--- | :--- | :--- | :--- |
| **Sites** | `contracts/sites.json` | `1.0` | Structural Dimension |
| **Equipment** | `contracts/equipment.json` | `1.0` | Structural Dimension |
| **Measurements** | `contracts/measurements.json` | `1.0` | Time-Series Fact |
| **Incidents** | `contracts/incidents.json` | `1.0` | Operational Log Fact |

## Contract Governance & Structural Responsibilities

Every declarative contract schema asset formally registers:
* **Required Column Fields:** Core structural columns necessary for down-stream processing loops.
* **Primitive Data Types:** Explicit type guards (e.g., `integer`, `decimal`, `timestamp`, `string`).
* **Nullability and Uniqueness Constraints:** Critical index rules enforced before loading rows.
* **Engineering Operating Ranges:** Domain-aware mathematical boundaries (e.g., packet loss between 0 and 100%).

## Schema Evolution & Change Management Guidelines

To ensure changes do not silently break downstream reporting tables or automated BI tools, follow this versioning standard:
1. **Patch Versions (`1.0.x`):** Cosmetic fixes, typo corrections, or descriptive comments inside documentation fields.
2. **Minor Versions (`1.x.0`):** Non-breaking changes, such as adding a new optional column or expanding a measurement range check.
3. **Major Versions (`2.0.0`):** Breaking schema mutations, such as deleting a required column, modifying a primary key constraint, or changing data types. Major updates require coordinate shifts across both upstream teams and downstream storage tiers.
