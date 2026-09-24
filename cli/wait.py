import time
from urllib import request

def wait_for_connect(url, timeout=180):
    endpoint = url.rstrip("/") + "/connector-plugins"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with request.urlopen(endpoint, timeout=5) as r:
                if r.status == 200:
                    print("[ready] Kafka Connect")
                    return
        except Exception:
            pass
        print("[wait] Kafka Connect...", flush=True)
        time.sleep(3)
    raise TimeoutError("Kafka Connect did not become ready")
