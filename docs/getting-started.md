# Getting Started Guide

Get the full Banking CDC Streaming Platform running on your local machine in under 3 minutes.

---

## Prerequisites

- **Docker Desktop** (or Docker Engine with Compose v2.20+)
- **Python 3.12+**
- Minimum **4GB RAM** allocated to Docker

---

## 1. Setup Environment

Clone the repository and install the development dependencies:

```bash
# 1. Clone repository
git clone https://github.com/TrNhDuong/Banking-Streaming.git
cd "Banking Streaming"

# 2. Install Python dependencies
python -m pip install -r requirements.txt

# 3. Create your local environment file
cp .env.local.example .env.local
```

*(On Windows PowerShell, use `Copy-Item .env.local.example .env.local`)*.

---

## 2. Launch the Platform (1-Click)

Run the local orchestrator:

```bash
python manage.py --env-file .env.local local up
```

### What happens automatically under the hood:
```text
[1/5] Starts PostgreSQL 16, Kafka KRaft, Kafka Connect, and Redpanda Console.
[2/5] Polls Kafka Connect REST API until healthy (waits for plugin initialization).
[3/5] Executes CDC setup on PostgreSQL: creates role 'debezium', grants replication, creates publication.
[4/5] Registers the Debezium connector via Kafka Connect REST API.
[5/5] Seeds 1,000 customers & 200 merchants, then starts streaming real-time transactions at 5 tx/s.
```

---

## 3. Verify System Health

### Option A — Web Console (Recommended)
Open your browser to:
👉 **[http://localhost:8080](http://localhost:8080)**

1. Navigate to **Topics**: You will see `banking.public.transactions` receiving messages.
2. Click on **Messages**: Click any live event to inspect the JSON CDC payload.
3. Navigate to **Kafka Connect**: Verify that connector `banking-cdc` is green (**RUNNING**).

### Option B — Check via CLI
```bash
# Check connector and task status
python manage.py connector status

# Check all container states
python manage.py local status
```

### Option C — Stream Live Transaction Logs
```bash
docker compose --env-file .env.local -f infra/docker-compose.local.yml logs -f generator
```

---

## 4. Run Offline Unit Tests

You can run the full suite of **81 unit tests** without starting Docker:

```bash
python -m pytest
```

Output:
```text
81 passed in 0.16s
```

---

## 5. Shut Down & Cleanup

When you are done testing:

```bash
# Stop containers (preserves database data)
python manage.py local down

# OR: Complete reset (wipes all containers and persistent volumes)
python manage.py local reset
```
