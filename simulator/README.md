# Banking Environment Simulator

This directory contains the **Core Banking Simulation Environment** used for local development, integration testing, and live portfolio demonstrations.

> [!NOTE]
> **Production Boundary**: In a real production deployment, this entire directory is **excluded**. The streaming CDC pipeline connects directly to the actual production banking database, and transactions originate from real customer applications.

---

## Components

### 1. `database/` (Mock Core Banking Database)
- **`schema.sql`**: PostgreSQL DDL defining banking entities:
  - `customers`: Customer profiles (`customer_id`, `full_name`, `email`).
  - `accounts`: Bank accounts (`account_id`, `customer_id`, `balance`, `status`).
  - `merchants`: Payment merchant entities.
  - `transactions`: Core ledger transactions (`transaction_id`, `from_account_id`, `to_account_id`, `amount`, `status`, `failure_reason`).
- **`Dockerfile`**: PostgreSQL 16 image pre-loaded with `schema.sql` for 1-click local setup.

### 2. `generator/` (Synthetic Transaction Producer)
- **Daemon service** that seeds initial data and streams realistic transactions:
  - Generates synthetic Vietnamese names and emails via `Faker(locale="vi_VN")`.
  - Simulates end-to-end transaction lifecycle: inserts as `PENDING`, waits briefly (simulating processing delay), then resolves to `SUCCESS` or `FAILED` (configurable failure rate).
  - Emits structured ISO timestamp logs and periodic throughput statistics.
