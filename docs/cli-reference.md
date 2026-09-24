# CLI Reference (`manage.py`)

The platform CLI provides a single entry point for orchestrating local containers, managing database CDC permissions, and interacting with Kafka Connect REST APIs.

---

## 1. Syntax Overview

```bash
python manage.py [--env-file <path>] [-v] [--log-file <path>] <group> <action>
```

### Global Options

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--env-file` | `.env.local` | Path to environment variable file to load. |
| `-v`, `--verbose` | `false` | Enable verbose `[DEBUG]` level logging. |
| `--log-file` | `None` | Optional file path to append structured log outputs. |
| `-h`, `--help` | — | Display command help and exit. |

---

## 2. Command Groups & Actions

### Group: `local` (Local Docker Orchestration)

Manage the local Docker Compose development stack.

```bash
# 1-Click Launch: Start all containers, configure CDC, apply connector, and seed
python manage.py local up

# Display status and port mappings for running containers
python manage.py local status

# Gracefully stop containers without destroying persistent volumes
python manage.py local down

# Complete reset: destroy containers, networks, and purge all data volumes
python manage.py local reset
```

---

### Group: `cdc` (Database CDC Management)

Manage PostgreSQL replication roles, permissions, and publications.

```bash
# Execute CDC setup SQL directly on the target database (Local dev only)
python manage.py cdc setup

# Verify PostgreSQL wal_level, publications, and replication slot status
python manage.py cdc verify

# Render CDC SQL DDL to stdout without executing (for DBA production review)
python manage.py --env-file .env.production cdc render
```

---

### Group: `connector` (Kafka Connect REST API)

Manage Debezium connector configurations via the Kafka Connect REST API.

```bash
# Deploy or update the Debezium connector configuration (HTTP PUT)
python manage.py connector apply

# Check health and task execution status of the connector (HTTP GET)
python manage.py connector status

# Delete the connector and stop CDC ingestion (HTTP DELETE)
python manage.py connector delete
```

---

## 3. Environment Variables Reference

| Variable | Default | Scope | Description |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | `local` | Global | Runtime environment indicator (`local` or `production`). |
| `DB_HOST` | `postgres` | CDC | PostgreSQL hostname or RDS endpoint. |
| `DB_PORT` | `5432` | CDC | PostgreSQL service port. |
| `DB_NAME` | `banking` | CDC | Target database name. |
| `DB_USER` | `debezium` | CDC | Username for CDC logical replication. |
| `DB_PASSWORD` | — | CDC | Password for CDC user. |
| `DB_SSLMODE` | `disable` | CDC | SSL mode: `disable` (local) or `require` (production). |
| `CDC_TABLES` | *(4 tables)* | CDC | Comma-separated list of tables to capture. |
| `CONNECTOR_NAME` | `banking-cdc` | Connector | Unique name of the connector in Kafka Connect. |
| `TOPIC_PREFIX` | `banking` | Connector | Prefix for generated Kafka topics (`banking.public.*`). |
| `SNAPSHOT_MODE` | `initial` | Connector | Snapshot behavior on startup (`initial` or `never`). |
| `CONNECT_REST_URL` | `http://localhost:8083` | Connect | Kafka Connect REST API endpoint. |
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:29092` | Kafka | Internal bootstrap servers string. |
| `KAFKA_UI_PORT` | `8080` | Infra | Host port for Redpanda Console web UI. |
| `GENERATOR_ENABLED` | `true` | Simulator | Toggle for synthetic transaction producer. |
| `TRANSACTIONS_PER_SECOND` | `5` | Simulator | Transaction generation rate. |
| `FAILURE_RATE` | `0.03` | Simulator | Probability of transaction resolving to `FAILED` (3%). |
