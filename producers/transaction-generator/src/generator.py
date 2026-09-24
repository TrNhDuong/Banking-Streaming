import logging
import os
import random
import time
import uuid
from decimal import Decimal

import psycopg

from .db import dsn

logger = logging.getLogger("generator")


def one() -> None:
    """Insert one PENDING transaction then resolve it to SUCCESS or FAILED."""
    failure_rate = float(os.getenv("FAILURE_RATE", "0.03"))
    try:
        with psycopg.connect(dsn()) as conn:
            with conn.cursor() as c:
                c.execute(
                    "SELECT account_id FROM accounts"
                    " WHERE status='ACTIVE' ORDER BY random() LIMIT 2"
                )
                rows = c.fetchall()
                if len(rows) < 2:
                    logger.warning(
                        "Not enough active accounts found (< 2). Waiting for active accounts."
                    )
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
                logger.info(
                    "Tx initiated: %s | %s -> %s | %s VND [PENDING]",
                    tx, a, b, f"{amt:,.0f}",
                )

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

                if failed:
                    logger.warning(
                        "Tx resolved:  %s | FAILED (reason: %s)", tx, reason
                    )
                else:
                    logger.info(
                        "Tx resolved:  %s | SUCCESS", tx
                    )
    except psycopg.Error as e:
        logger.error("Database error during transaction execution: %s", e)
    except Exception as e:
        logger.error("Unexpected error during transaction execution: %s", e, exc_info=True)
