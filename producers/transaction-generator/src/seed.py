import os
import random
import uuid
from decimal import Decimal

import psycopg
from faker import Faker

from .db import dsn

fake = Faker("vi_VN")


def seed() -> None:
    """Populate customers, accounts, and merchants if the DB is empty."""
    if os.getenv("SEED_ENABLED", "true").lower() != "true":
        return
    with psycopg.connect(dsn()) as conn:
        with conn.cursor() as c:
            c.execute("SELECT COUNT(*) FROM customers")
            if c.fetchone()[0]:
                return  # already seeded
            for _ in range(int(os.getenv("CUSTOMER_COUNT", "1000"))):
                cid = uuid.uuid4()
                c.execute(
                    "INSERT INTO customers(customer_id,full_name,email) VALUES(%s,%s,%s)",
                    (cid, fake.name(), fake.email()),
                )
                for __ in range(random.randint(1, 3)):
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
            for _ in range(int(os.getenv("MERCHANT_COUNT", "200"))):
                c.execute(
                    "INSERT INTO merchants(merchant_id,merchant_name) VALUES(%s,%s)",
                    (uuid.uuid4(), fake.company()),
                )
        conn.commit()
    print("[seed] done", flush=True)
