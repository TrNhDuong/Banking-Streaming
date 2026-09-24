import logging
import os
import random
import time
import uuid
from decimal import Decimal

import psycopg
from faker import Faker

from .db import dsn

logger = logging.getLogger("seed")
fake = Faker("vi_VN")


def seed() -> None:
    """Populate customers, accounts, and merchants if the DB is empty."""
    if os.getenv("SEED_ENABLED", "true").lower() != "true":
        logger.info("Database seeding skipped (SEED_ENABLED=false)")
        return

    customer_target = int(os.getenv("CUSTOMER_COUNT", "1000"))
    merchant_target = int(os.getenv("MERCHANT_COUNT", "200"))

    logger.info("Checking database seed status...")
    start_time = time.time()

    try:
        with psycopg.connect(dsn()) as conn:
            with conn.cursor() as c:
                c.execute("SELECT COUNT(*) FROM customers")
                existing_count = c.fetchone()[0]
                if existing_count > 0:
                    logger.info(
                        "Database already seeded (%d customers found). Skipping seed.",
                        existing_count,
                    )
                    return

                logger.info(
                    "Starting seed: generating %d customers and %d merchants...",
                    customer_target,
                    merchant_target,
                )

                total_accounts = 0
                for i in range(customer_target):
                    cid = uuid.uuid4()
                    c.execute(
                        "INSERT INTO customers(customer_id,full_name,email) VALUES(%s,%s,%s)",
                        (cid, fake.name(), fake.email()),
                    )
                    acc_count = random.randint(1, 3)
                    for _ in range(acc_count):
                        c.execute(
                            "INSERT INTO accounts"
                            "(account_id,customer_id,account_type,balance,status)"
                            " VALUES(%s,%s,%s,%s,'ACTIVE')",
                            (
                                uuid.uuid4(),
                                cid,
                                random.choice(["CHECKING", "SAVINGS"]),
                                Decimal(random.randint(1_000_000, 500_000_000)),
                            ),
                        )
                    total_accounts += acc_count

                for _ in range(merchant_target):
                    c.execute(
                        "INSERT INTO merchants(merchant_id,merchant_name) VALUES(%s,%s)",
                        (uuid.uuid4(), fake.company()),
                    )

            conn.commit()

        elapsed = time.time() - start_time
        logger.info(
            "Seed completed in %.2fs: created %d customers, %d accounts, %d merchants",
            elapsed,
            customer_target,
            total_accounts,
            merchant_target,
        )
    except Exception as e:
        logger.error("Failed to seed database: %s", e, exc_info=True)
        raise
