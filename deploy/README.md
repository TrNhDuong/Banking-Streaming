# Deploy Guide

Production deployment assumes PostgreSQL and Kafka are already running
(RDS, MSK, Confluent Cloud, or self-hosted).

## Prerequisites

| Component | Required | Notes |
|-----------|----------|-------|
| PostgreSQL | ✅ | `wal_level=logical` must be set |
| Kafka | ✅ | Any Kafka-compatible broker |
| Kafka Connect | deploy this | See steps below |

---

## Step 1 — Configure environment

```bash
cp .env.production.example .env.production
# Fill in DB_HOST, DB_PASSWORD, KAFKA_BOOTSTRAP_SERVERS, CONNECT_REST_URL, etc.
```

---

## Step 2 — DBA: CDC setup on PostgreSQL

Generate the SQL and hand it to the DBA to run on the production DB:

```bash
python platform.py --env-file .env.production cdc render > cdc_setup.sql
# Review cdc_setup.sql, then execute on the production PostgreSQL instance
```

This creates:
- Debezium replication user
- Logical replication publication

---

## Step 3 — Build & push Kafka Connect image

```bash
# Build
docker build deploy/connect/ -t banking-connect:latest

# Tag & push to your registry
docker tag banking-connect:latest <registry>/banking-connect:latest
docker push <registry>/banking-connect:latest
```

---

## Step 4 — Deploy Kafka Connect

### Option A — Docker on a VM

```bash
docker compose --env-file .env.production \
  -f deploy/docker-compose.prod.yml up -d
```

### Option B — AWS ECS

Use `deploy/connect/Dockerfile` and `deploy/docker-compose.prod.yml` as reference
for environment variables when creating the ECS Task Definition.

### Option C — Kubernetes

Use `deploy/docker-compose.prod.yml` environment variables as reference
for the K8s Deployment manifest and ConfigMap/Secret.

---

## Step 5 — Register Debezium connector

Once Kafka Connect is running at `CONNECT_REST_URL`:

```bash
python platform.py --env-file .env.production connector apply
```

---

## Step 6 — Verify

```bash
python platform.py --env-file .env.production connector status
```

---

## Re-deploy / Update connector config

Re-run Step 5 at any time to update the connector configuration.
The `connector apply` command uses HTTP PUT — safe to run multiple times.
