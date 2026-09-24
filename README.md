# Banking CDC Platform

PostgreSQL → Debezium → Kafka streaming pipeline with a CLI-first local workflow.

## Stack

- **Source DB**: PostgreSQL (logical WAL + pgoutput)
- **CDC**: Debezium via Kafka Connect
- **Broker**: Apache Kafka (KRaft mode)
- **Producer**: synthetic transaction generator (`vi_VN` locale)

## Local

```bash
python -m pip install -r requirements.txt
cp .env.local.example .env.local

python manage.py --env-file .env.local local up
python manage.py --env-file .env.local local status
python manage.py --env-file .env.local cdc verify
python manage.py --env-file .env.local connector status
python manage.py --env-file .env.local local down
```

`local up` starts Kafka + Kafka Connect + PostgreSQL, runs CDC setup,
registers the Debezium connector, and starts the transaction generator.

> **Note:** The transaction generator is PostgreSQL-only. It seeds
> 1 000 customers, 200 merchants, and then streams transactions at the
> configured rate with a configurable failure rate.

## Individual stages

```bash
python manage.py --env-file .env.local cdc setup
python manage.py --env-file .env.local connector apply
```

## Render DBA SQL (production)

For a production/existing DB, render the DBA prerequisites without executing:

```bash
python manage.py --env-file .env.production cdc render
```

## External Kafka

Set `KAFKA_BOOTSTRAP_SERVERS` in your env file when the schema-history
topic needs to point at an external Kafka cluster (default: `kafka:29092`).
