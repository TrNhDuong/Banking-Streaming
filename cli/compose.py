from .process import run

COMPOSE_FILE = "infra/docker-compose.local.yml"


def compose(env_file, args):
    run(["docker", "compose", "--env-file", env_file, "-f", COMPOSE_FILE, *args])


def up_core(env_file):
    compose(env_file, ["--profile", "postgres", "up", "-d", "--build", "kafka", "connect", "postgres"])


def up_generator(env_file):
    compose(env_file, ["--profile", "postgres", "up", "-d", "--build", "generator"])


def down(env_file):
    compose(env_file, ["down", "--remove-orphans"])


def reset(env_file):
    compose(env_file, ["down", "-v", "--remove-orphans"])


def status(env_file):
    compose(env_file, ["ps"])
