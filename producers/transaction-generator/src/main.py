import os
import time

from .seed import seed
from .generator import one


def main() -> None:
    seed()
    rate = max(float(os.getenv("TRANSACTIONS_PER_SECOND", "5")), 0.1)
    print(f"[generator] running at {rate} tx/s", flush=True)
    while True:
        one()
        time.sleep(1 / rate)


if __name__ == "__main__":
    main()
