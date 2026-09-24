import json
from urllib import request, error
from .env import env
from .connectors import build


def call(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(url, method=method, data=data, headers=headers)
    try:
        with request.urlopen(req, timeout=20) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else None
    except error.HTTPError as e:
        raw = e.read()
        try:
            body = json.loads(raw) if raw else None
        except Exception:
            body = raw.decode(errors="replace")
        return e.code, body


def apply():
    base = env("CONNECT_REST_URL", "http://localhost:8083").rstrip("/")
    name = env("CONNECTOR_NAME", "banking-cdc")
    code, body = call("PUT", f"{base}/connectors/{name}/config", build())
    print(json.dumps(body, indent=2) if body is not None else "")
    if code not in {200, 201}:
        raise SystemExit(f"HTTP {code}")


def status():
    base = env("CONNECT_REST_URL", "http://localhost:8083").rstrip("/")
    name = env("CONNECTOR_NAME", "banking-cdc")
    code, body = call("GET", f"{base}/connectors/{name}/status")
    print(json.dumps(body, indent=2) if body is not None else "")
    if code != 200:
        raise SystemExit(f"HTTP {code}")


def delete():
    base = env("CONNECT_REST_URL", "http://localhost:8083").rstrip("/")
    name = env("CONNECTOR_NAME", "banking-cdc")
    code, body = call("DELETE", f"{base}/connectors/{name}")
    if body is not None:
        print(json.dumps(body, indent=2))
    if code not in {200, 204, 404}:
        raise SystemExit(f"HTTP {code}")
