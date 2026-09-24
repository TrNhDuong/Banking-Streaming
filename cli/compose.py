import time
from urllib import request

from .process import run
from .logger import get_logger

COMPOSE_FILE = "infra/docker-compose.local.yml"
logger = get_logger("compose")


def compose(env_file: str, args: list[str]) -> None:
    run(["docker", "compose", "--env-file", env_file, "-f", COMPOSE_FILE, *args])


def up_core(env_file: str) -> None:
    compose(env_file, ["--profile", "postgres", "up", "-d", "--build", "kafka", "connect", "postgres"])


def up_generator(env_file: str) -> None:
    compose(env_file, ["--profile", "postgres", "up", "-d", "--build", "generator"])


def down(env_file: str) -> None:
    compose(env_file, ["down", "--remove-orphans"])


def reset(env_file: str) -> None:
    compose(env_file, ["down", "-v", "--remove-orphans"])


def status(env_file: str) -> None:
    compose(env_file, ["ps"])


def wait_for_connect(url: str, timeout: int = 180) -> None:
    """Poll Kafka Connect REST API until it responds 200 or timeout expires."""
    endpoint = url.rstrip("/") + "/connector-plugins"
    deadline = time.time() + timeout
    attempt = 1
    while time.time() < deadline:
        try:
            with request.urlopen(endpoint, timeout=5) as r:
                if r.status == 200:
                    logger.info("Kafka Connect is online and responsive.")
                    return
        except Exception:
            pass
        logger.info("Waiting for Kafka Connect to initialize (attempt #%d)...", attempt)
        attempt += 1
        time.sleep(3)
    logger.error("Kafka Connect did not become ready within %ds", timeout)
    raise TimeoutError("Kafka Connect did not become ready")
