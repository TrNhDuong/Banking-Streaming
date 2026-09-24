# Local Infrastructure

This directory contains the modular Docker Compose configurations for running the end-to-end streaming stack locally.

## Architecture

The local stack is composed via `docker-compose.local.yml` using the Docker Compose `include:` directive (Compose v2.20+):

| Subdirectory | Service | Port | Description |
| :--- | :--- | :--- | :--- |
| `kafka/` | `kafka` | `9092` | Apache Kafka broker (KRaft mode, no Zookeeper required) |
| `kafka/` | `kafka-ui` | `8080` | Redpanda Console web UI for inspecting topics, schemas, and consumer groups |
| `debezium/` | `connect` | `8083` | Kafka Connect distributed runner (builds from `deploy/connect/Dockerfile`) |
| `postgres/` | `postgres` | `5432` | PostgreSQL 16 with logical replication enabled (`wal_level=logical`) |
| `postgres/` | `generator` | — | Background synthetic transaction generator from `simulator/generator/` |

---

## Usage via CLI

Manage the entire local stack with a single command via [manage.py](file:///c:/Users/MY%20MSI/Desktop/Project/Data%20Engineer/Banking%20Streaming/manage.py):

```bash
# Start all services, configure CDC, and apply connector
python manage.py --env-file .env.local local up

# Check status of running containers
python manage.py --env-file .env.local local status

# Stop containers without losing data
python manage.py --env-file .env.local local down

# Reset stack completely (destroys containers and volume data)
python manage.py --env-file .env.local local reset
```

## Kafka UI

Once running, navigate to:
```text
http://localhost:8080
```
to view topics (`banking.public.transactions`, `banking.public.customers`, etc.), message payloads, and connector health in real time.
