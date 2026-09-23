"""One-shot synthetic scenario control and bounded evidence reader."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import urllib.parse
import urllib.request


APP = "http://app:8080"
PROMETHEUS = "http://prometheus:9090"
CONTROL_MARKER = "synthetic-only"
QUERIES = {
    "request_rate_per_second": 'sum(rate(lab_http_requests_total{route="/quotes"}[1m]))',
    "error_ratio": 'sum(rate(lab_http_requests_total{route="/quotes",status=~"5.."}[1m])) / clamp_min(sum(rate(lab_http_requests_total{route="/quotes"}[1m])), 0.001)',
    "p95_latency_seconds": 'histogram_quantile(0.95, sum by (le) (rate(lab_http_request_duration_seconds_bucket{route="/quotes"}[1m])))',
    "degraded_mode": 'lab_mode{mode="degraded"}',
}


def opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def read_json(url: str) -> object:
    with opener().open(url, timeout=2) as response:
        payload = response.read(65537)
    if len(payload) > 65536:
        raise RuntimeError("response exceeded 64 KiB")
    return json.loads(payload)


def change(action: str) -> object:
    body = json.dumps({"action": action}).encode("utf-8")
    request = urllib.request.Request(
        APP + "/control",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "X-Lab-Control": CONTROL_MARKER},
    )
    with opener().open(request, timeout=2) as response:
        payload = response.read(4097)
    if len(payload) > 4096:
        raise RuntimeError("control response exceeded 4 KiB")
    return json.loads(payload)


def evidence() -> dict[str, object]:
    results: dict[str, object] = {}
    for name, query in QUERIES.items():
        url = PROMETHEUS + "/api/v1/query?" + urllib.parse.urlencode({"query": query})
        payload = read_json(url)
        if not isinstance(payload, dict) or payload.get("status") != "success":
            raise RuntimeError(f"Prometheus query failed: {name}")
        results[name] = payload.get("data", {}).get("result", [])
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "synthetic": True,
        "app": read_json(APP + "/state"),
        "prometheus": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Control the synthetic lab")
    parser.add_argument("action", choices=("degrade", "recover", "reset", "evidence"))
    args = parser.parse_args()
    result = evidence() if args.action == "evidence" else change(args.action)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
