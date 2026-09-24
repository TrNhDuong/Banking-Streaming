import logging
import os
import signal
import sys
import time

from .generator import one
from .logger import setup_logging
from .seed import seed

logger = logging.getLogger("main")


def main() -> None:
    root_logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Banking Transaction Generator Service Starting...")
    logger.info("=" * 60)

    try:
        seed()
    except Exception as e:
        logger.critical("Seed phase failed, shutting down generator: %s", e)
        sys.exit(1)

    rate = max(float(os.getenv("TRANSACTIONS_PER_SECOND", "5")), 0.1)
    failure_rate = float(os.getenv("FAILURE_RATE", "0.03"))
    interval = 1.0 / rate

    logger.info(
        "Generator loop started: target_rate=%.1f tx/s (interval=%.3fs), failure_rate=%.1f%%",
        rate,
        interval,
        failure_rate * 100,
    )

    tx_count = 0
    start_time = time.time()

    def handle_signal(sig, frame):
        logger.info("Received termination signal (%s). Shutting down gracefully...", sig)
        elapsed = time.time() - start_time
        logger.info(
            "Generator shutdown summary: processed %d transactions in %.1fs (avg %.2f tx/s)",
            tx_count,
            elapsed,
            tx_count / elapsed if elapsed > 0 else 0,
        )
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        while True:
            one()
            tx_count += 1
            if tx_count % 100 == 0:
                elapsed = time.time() - start_time
                avg_rate = tx_count / elapsed if elapsed > 0 else 0
                logger.info(
                    "Heartbeat: %d transactions generated so far (avg %.2f tx/s)",
                    tx_count,
                    avg_rate,
                )
            time.sleep(interval)
    except KeyboardInterrupt:
        handle_signal(signal.SIGINT, None)


if __name__ == "__main__":
    main()
