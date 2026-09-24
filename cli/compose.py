import time
from urllib import request

from .process import run

COMPOSE_FILE = "infra/docker-compose.local.yml"


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
    while time.time() < deadline:
        try:
            with request.urlopen(endpoint, timeout=5) as r:
                if r.status == 200:
                    print("[ready] Kafka Connect", flush=True)
                    return
        except Exception:
            pass
        print("[wait] Kafka Connect...", flush=True)
        time.sleep(3)
    raise TimeoutError("Kafka Connect did not become ready")
