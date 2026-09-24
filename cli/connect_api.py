import json
from urllib import request, error
from .env import env
from .connectors import build
from .logger import get_logger

logger = get_logger("connect_api")


def call(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(url, method=method, data=data, headers=headers)
    logger.debug("REST request: %s %s", method, url)
    try:
        with request.urlopen(req, timeout=20) as r:
            raw = r.read()
            body = json.loads(raw) if raw else None
            logger.debug("REST response: HTTP %s", r.status)
            return r.status, body
    except error.HTTPError as e:
        raw = e.read()
        try:
            body = json.loads(raw) if raw else None
        except Exception:
            body = raw.decode(errors="replace")
        logger.debug("REST HTTP error: HTTP %s - %s", e.code, body)
        return e.code, body


def apply():
    base = env("CONNECT_REST_URL", "http://localhost:8083").rstrip("/")
    name = env("CONNECTOR_NAME", "banking-cdc")
    logger.info("Configuring connector '%s' at %s...", name, base)
    code, body = call("PUT", f"{base}/connectors/{name}/config", build())
    print(json.dumps(body, indent=2) if body is not None else "")
    if code in {200, 201}:
        logger.info("Connector '%s' applied successfully (HTTP %d).", name, code)
    else:
        logger.error("Failed to apply connector '%s' (HTTP %d)", name, code)
        raise SystemExit(f"HTTP {code}")


def status():
    base = env("CONNECT_REST_URL", "http://localhost:8083").rstrip("/")
    name = env("CONNECTOR_NAME", "banking-cdc")
    logger.info("Fetching status for connector '%s'...", name)
    code, body = call("GET", f"{base}/connectors/{name}/status")
    print(json.dumps(body, indent=2) if body is not None else "")
    if code == 200:
        logger.info("Connector '%s' status fetched successfully.", name)
    else:
        logger.error("Failed to fetch status for '%s' (HTTP %d)", name, code)
        raise SystemExit(f"HTTP {code}")


def delete():
    base = env("CONNECT_REST_URL", "http://localhost:8083").rstrip("/")
    name = env("CONNECTOR_NAME", "banking-cdc")
    logger.info("Deleting connector '%s'...", name)
    code, body = call("DELETE", f"{base}/connectors/{name}")
    if body is not None:
        print(json.dumps(body, indent=2))
    if code in {200, 204, 404}:
        logger.info("Connector '%s' deleted (HTTP %d).", name, code)
    else:
        logger.error("Failed to delete connector '%s' (HTTP %d)", name, code)
        raise SystemExit(f"HTTP {code}")
