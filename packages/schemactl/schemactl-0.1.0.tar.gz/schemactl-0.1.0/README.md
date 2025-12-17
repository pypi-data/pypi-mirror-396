# schemactl

> **framework‑agnostic database schema evolution tool for Python**

`schemactl` is a next‑generation database migration tool built on top of **SQLAlchemy metadata** and **Alembic autogeneration**.

Unlike traditional migration tools, `schemactl` is designed as a **schema evolution engine**, not just a migration runner. It is architecture‑first, deterministic, and ready to integrate with **LLMs, agents, and autonomous workflows**.

---

## Why schemactl?

Most migration tools are:

* framework‑coupled
* imperative and manual
* hard to reason about at scale
* unfriendly to AI‑assisted workflows

`schemactl` takes a different approach:

* **Framework‑agnostic** – works with pure SQLAlchemy
* **Metadata‑driven** – schema is the single source of truth
* **Diff‑based** – migrations are generated from real schema changes
* **Deterministic** – reproducible and auditable
* **AI‑ready** – designed for LLM review, risk analysis, and human‑in‑the‑loop control

---

## Core Concepts

### Schema as Code

Your SQLAlchemy models (metadata) define the desired state of the database.

```python
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String, unique=True)
```

`schemactl` compares this metadata against the actual database schema and generates migrations automatically.

---

### Evolution, Not Just Migration

Instead of thinking in terms of *"apply SQL files"*, `schemactl` models:

* schema **diffs**
* schema **versions**
* schema **state**

This enables future features like:

* automated rollback planning
* migration safety scoring
* AI‑assisted reviews
* policy enforcement

---

## Installation

```bash
pip install schemactl
```

---

## CLI Overview

```bash
schemactl --help
```

Planned commands:

```text
schemactl new       # generate a new migration from metadata diff
schemactl up        # create DB (if needed) and apply pending migrations
schemactl create    # create the database
schemactl drop      # drop the database
schemactl migrate   # run pending migrations
schemactl rollback  # rollback the last migration
schemactl down      # alias for rollback
schemactl status    # show migration status
#schemactl dump      # dump schema.sql
#schemactl load      # load schema.sql
schemactl wait      # wait for DB readiness
```


---

## Usage

### 1. Generate a Migration

```bash
schemactl new \
  --message add_users_table
```

What happens:

1. Connects to the database
2. Loads SQLAlchemy metadata
3. Uses Alembic autogenerate to compute schema diff
4. Creates a new migration file under:

```text
migrations/
└── versions/
    └── 20250101123000_add_users_table.py
```

---

### 2. Apply Migrations

```bash
schemactl up
```

What happens:

* Creates the database if it does not exist
* Ensures the `schema_migrations` table exists
* Applies all pending migrations in order
* Records applied revisions deterministically

---

## Project Structure

```text
.
├── schemactl/              # Main package source
│   ├── cli.py              # CLI commands
│   ├── services/           # Business logic and services
│   │   └── migration.py
│   │   └── model_loader.py
│   ├── adapters/           # Database and Alembic adapters
│   │   ├── alembic.py
│   │   └── database.py
├── migrations/             # Generated migration files
├── tests/                  # Unit and integration tests
├── pyproject.toml          # Project configuration (Poetry)
└── poetry.lock             # Poetry lock file
```

This structure follows **Clean Architecture** and keeps infrastructure concerns isolated.

---

## Design Principles

* Architecture first, code second
* Prefer declarative over imperative
* Explicit state tracking
* Simple core, extensible edges

---

## Status

⚠️ **Early development / experimental**

APIs may change.
Migration format is not yet stable.

---

## License

MIT

---

## Contributing

Contributions are welcome, especially in:

* migration safety
* rollback logic
* Async / cloud databases

Design discussions > code dumps.
