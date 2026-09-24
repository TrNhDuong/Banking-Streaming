# CDC Event Specification

This document details the exact JSON envelope and payload format produced by Debezium into Kafka topics. Downstream consumers (Spark, Flink, Kafka Streams, microservices) should parse events according to this specification.

---

## 1. Topic Naming Convention

Debezium names topics using the pattern:
```text
<TOPIC_PREFIX>.<SCHEMA_NAME>.<TABLE_NAME>
```

In this platform (`TOPIC_PREFIX=banking`):

| Database Table | Kafka Topic Name | Event Content |
| :--- | :--- | :--- |
| `public.transactions` | `banking.public.transactions` | Financial transactions (PENDING, SUCCESS, FAILED) |
| `public.accounts` | `banking.public.accounts` | Account balances and status updates |
| `public.customers` | `banking.public.customers` | Customer registration and profile changes |
| `public.merchants` | `banking.public.merchants` | Merchant profiles |

---

## 2. Event Envelope Structure

Each message contains two top-level sections:
1. **`schema`**: Formal struct definition with data types, nullability, and field metadata.
2. **`payload`**: The actual CDC event data.

```json
{
  "schema": { "type": "struct", "fields": [ ... ] },
  "payload": {
    "before": { ... },     // State of row BEFORE the change (null on INSERT)
    "after":  { ... },     // State of row AFTER the change (null on DELETE)
    "source": { ... },     // PostgreSQL WAL metadata (LSN, txId, timestamp)
    "op":     "c",         // Operation code: c, u, d, or r
    "ts_ms":  1790237770   // Timestamp when Debezium processed the event
  }
}
```

---

## 3. Operation Codes (`op`)

| Code | Operation | Meaning | `before` | `after` |
| :---: | :--- | :--- | :---: | :---: |
| **`c`** | **Create** | New row inserted (`INSERT`) | `null` | New values |
| **`u`** | **Update** | Existing row updated (`UPDATE`) | Old values | New values |
| **`d`** | **Delete** | Row deleted (`DELETE`) | Old values | `null` |
| **`r`** | **Read** | Snapshot record from initial table dump | `null` | Existing values |

---

## 4. Real-World Banking CDC Lifecycle Example

In this platform, a money transfer generates **two consecutive events** with the same `transaction_id`.

### Step 1: Transaction Created (`op: "c"`, status: `PENDING`)
```json
{
  "payload": {
    "before": null,
    "after": {
      "transaction_id": "7c2f3b61-cb1c-4f91-89a7-b28d87c5cadc",
      "from_account_id": "3499d75c-0506-4997-98c4-88dfc7668584",
      "to_account_id": "0a34a8ca-52b9-4cdb-83e2-8d94ca5960c2",
      "transaction_type": "TRANSFER",
      "amount": "1955293.00",
      "status": "PENDING",
      "failure_reason": null,
      "created_at": "2026-09-24T08:16:10.282720Z"
    },
    "source": {
      "connector": "postgresql",
      "db": "banking",
      "table": "transactions",
      "lsn": 28148296,
      "txId": 2145,
      "snapshot": "false"
    },
    "op": "c"
  }
}
```

### Step 2: Transaction Resolved (`op: "u"`, status: `SUCCESS`)
```json
{
  "payload": {
    "before": {
      "transaction_id": "7c2f3b61-cb1c-4f91-89a7-b28d87c5cadc",
      "status": "PENDING"
    },
    "after": {
      "transaction_id": "7c2f3b61-cb1c-4f91-89a7-b28d87c5cadc",
      "from_account_id": "3499d75c-0506-4997-98c4-88dfc7668584",
      "to_account_id": "0a34a8ca-52b9-4cdb-83e2-8d94ca5960c2",
      "transaction_type": "TRANSFER",
      "amount": "1955293.00",
      "status": "SUCCESS",
      "failure_reason": null,
      "created_at": "2026-09-24T08:16:10.282720Z"
    },
    "source": {
      "connector": "postgresql",
      "db": "banking",
      "table": "transactions",
      "lsn": 28150420,
      "txId": 2146,
      "snapshot": "false"
    },
    "op": "u"
  }
}
```

---

## 5. Consumer Recommendations

1. **Ordering by Key**: Events for the same table row share the same Kafka message key (`transaction_id`), guaranteeing strict chronological delivery within a Kafka partition.
2. **Idempotency**: Use `payload.after.transaction_id` + `payload.after.status` (or `source.lsn`) as an idempotency deduplication key.
3. **Filtering Deletes**: When `payload.op == "d"`, check `payload.before` for the identifier of the deleted record.
