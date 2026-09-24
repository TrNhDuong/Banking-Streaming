import subprocess
from .logger import get_logger

logger = get_logger("process")


def run(args, input_text=None):
    logger.info("$ %s", " ".join(args))
    return subprocess.run(args, input=input_text, text=True, check=True)
