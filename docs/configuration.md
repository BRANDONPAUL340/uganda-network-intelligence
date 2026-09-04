# Configuration Management

The Uganda Network & Service Intelligence Platform uses decoupled environment variables for secure, portable database configuration.

## Local Configuration

To run the pipeline locally, provision a `.env` file in the project root directory:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=network_intelligence
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
```

## Security Perimeter Contracts

* **Exclusion Isolation:** The `.env` file contains sensitive local credentials and is strictly excluded from version control tracking via `.gitignore`.
* **Zero-Leak Governance:** Plaintext database passwords, credentials, or explicit connection strings must **never** be committed to public repository branches.
* **Blueprint Templates:** The `.env.example` file is safely tracked in Git, providing a clean placeholder template for onboarding collaborators.

## Configuration Data Flow Lineage

```text
  [Local `.env` File]
           │
           ▼
    [src/config.py]     ◄── Parses strings and runs validation guards
           │
           ▼
   [src/database.py]    ◄── Compiles dynamic URL and handles pool pre-pings
           │
           ▼
     [SQLAlchemy]       ◄── Bridges object-relational mapping models
           │
           ▼
     [PostgreSQL]       ◄── Final physical storage disk engine
```
