import os
import random
import time
import uuid
from decimal import Decimal

import psycopg

from .db import dsn


def one() -> None:
    """Insert one PENDING transaction then resolve it to SUCCESS or FAILED."""
    failure_rate = float(os.getenv("FAILURE_RATE", "0.03"))
    with psycopg.connect(dsn()) as conn:
        with conn.cursor() as c:
            c.execute(
                "SELECT account_id FROM accounts"
                " WHERE status='ACTIVE' ORDER BY random() LIMIT 2"
            )
            rows = c.fetchall()
            if len(rows) < 2:
                return
            a, b = rows[0][0], rows[1][0]
            amt = Decimal(random.randint(10_000, 2_000_000))
            tx = uuid.uuid4()
            c.execute(
                "INSERT INTO transactions"
                "(transaction_id,from_account_id,to_account_id,transaction_type,amount,status)"
                " VALUES(%s,%s,%s,'TRANSFER',%s,'PENDING')",
                (tx, a, b, amt),
            )
            conn.commit()

            time.sleep(0.2)  # simulate processing delay

            failed = random.random() < failure_rate
            status = "FAILED" if failed else "SUCCESS"
            reason = "Insufficient funds simulation" if failed else None
            c.execute(
                "UPDATE transactions SET status=%s,failure_reason=%s"
                " WHERE transaction_id=%s",
                (status, reason, tx),
            )
            conn.commit()
