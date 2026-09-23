"""Synthetic, bounded observability target for the local training lab."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import signal
import threading
import time
from urllib.parse import urlsplit


CONTROL_MARKER = "synthetic-only"
BUCKETS = (0.025, 0.05, 0.1, 0.25, 0.5, 1.0)


class LabState:
    """Owns the only mutable state; all values are synthetic and in memory."""

    def __init__(self, *, emit_logs: bool = True) -> None:
        self._lock = threading.Lock()
        self._mode = "healthy"
        self._quote_sequence = 0
        self._requests: Counter[tuple[str, str, str]] = Counter()
        self._duration_count: Counter[tuple[str, str]] = Counter()
        self._duration_sum: defaultdict[tuple[str, str], float] = defaultdict(float)
        self._duration_buckets: Counter[tuple[str, str, float]] = Counter()
        self._resets = 0
        self._started_at = time.time()
        self.emit_logs = emit_logs

    def mode(self) -> str:
        with self._lock:
            return self._mode

    def change(self, action: str) -> dict[str, object]:
        if action not in {"degrade", "recover", "reset"}:
            raise ValueError("unknown action")
        with self._lock:
            if action == "degrade":
                self._mode = "degraded"
            elif action == "recover":
                self._mode = "healthy"
            else:
                self._mode = "healthy"
                self._quote_sequence = 0
                self._requests.clear()
                self._duration_count.clear()
                self._duration_sum.clear()
                self._duration_buckets.clear()
                self._resets += 1
            return {"action": action, "mode": self._mode, "resets_total": self._resets}

    def quote(self) -> tuple[int, dict[str, object], float, str, int]:
        with self._lock:
            self._quote_sequence += 1
            sequence = self._quote_sequence
            mode = self._mode

        started = time.monotonic()
        if mode == "degraded":
            time.sleep(0.35)
            status = 200 if sequence % 4 == 0 else 503
        else:
            time.sleep(0.02)
            status = 200
        duration = time.monotonic() - started
        body: dict[str, object]
        if status == 200:
            body = {"symbol": "DEMO", "value": 100, "synthetic": True, "mode": mode}
        else:
            body = {"error": "synthetic upstream timeout", "synthetic": True, "mode": mode}
        self.observe("/quotes", status, mode, duration)
        return status, body, duration, mode, sequence

    def observe(self, route: str, status: int, mode: str, duration: float) -> None:
        with self._lock:
            self._requests[(route, str(status), mode)] += 1
            self._duration_count[(route, mode)] += 1
            self._duration_sum[(route, mode)] += duration
            for bucket in BUCKETS:
                if duration <= bucket:
                    self._duration_buckets[(route, mode, bucket)] += 1

    def summary(self) -> dict[str, object]:
        with self._lock:
            total = sum(self._requests.values())
            errors = sum(
                count for (_, status, _), count in self._requests.items() if status.startswith("5")
            )
            return {
                "mode": self._mode,
                "requests_total": total,
                "errors_total": errors,
                "resets_total": self._resets,
                "synthetic": True,
            }

    def prometheus(self) -> str:
        with self._lock:
            mode = self._mode
            requests = sorted(self._requests.items())
            duration_count = sorted(self._duration_count.items())
            duration_sum = dict(self._duration_sum)
            duration_buckets = dict(self._duration_buckets)
            resets = self._resets
            started_at = self._started_at

        lines = [
            "# HELP lab_http_requests_total Synthetic HTTP requests handled.",
            "# TYPE lab_http_requests_total counter",
        ]
        for (route, status, request_mode), value in requests:
            lines.append(
                f'lab_http_requests_total{{route="{route}",status="{status}",mode="{request_mode}"}} {value}'
            )
        lines.extend(
            [
                "# HELP lab_http_request_duration_seconds Synthetic request duration.",
                "# TYPE lab_http_request_duration_seconds histogram",
            ]
        )
        for (route, request_mode), count in duration_count:
            for bucket in BUCKETS:
                cumulative = duration_buckets.get((route, request_mode, bucket), 0)
                lines.append(
                    f'lab_http_request_duration_seconds_bucket{{route="{route}",mode="{request_mode}",le="{bucket:g}"}} {cumulative}'
                )
            lines.append(
                f'lab_http_request_duration_seconds_bucket{{route="{route}",mode="{request_mode}",le="+Inf"}} {count}'
            )
            lines.append(
                f'lab_http_request_duration_seconds_sum{{route="{route}",mode="{request_mode}"}} {duration_sum[(route, request_mode)]:.6f}'
            )
            lines.append(
                f'lab_http_request_duration_seconds_count{{route="{route}",mode="{request_mode}"}} {count}'
            )
        lines.extend(
            [
                "# HELP lab_mode Current synthetic mode (one active series).",
                "# TYPE lab_mode gauge",
                f'lab_mode{{mode="healthy"}} {1 if mode == "healthy" else 0}',
                f'lab_mode{{mode="degraded"}} {1 if mode == "degraded" else 0}',
                "# HELP lab_resets_total Idempotent reset commands received.",
                "# TYPE lab_resets_total counter",
                f"lab_resets_total {resets}",
                "# HELP lab_process_start_time_seconds Synthetic process start time.",
                "# TYPE lab_process_start_time_seconds gauge",
                f"lab_process_start_time_seconds {started_at:.3f}",
            ]
        )
        return "\n".join(lines) + "\n"

    def log(self, event: dict[str, object]) -> None:
        if self.emit_logs:
            print(json.dumps(event, separators=(",", ":"), sort_keys=True), flush=True)


def make_handler(state: LabState) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "SyntheticLab/1.0"
        sys_version = ""

        def log_message(self, *_: object) -> None:
            return

        def _send_json(self, status: int, payload: dict[str, object]) -> None:
            body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            if path == "/health":
                self._send_json(200, {"status": "process-running", "synthetic": True})
                return
            if path == "/state":
                self._send_json(200, state.summary())
                return
            if path == "/metrics":
                body = state.prometheus().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if path == "/quotes":
                status, payload, duration, mode, sequence = state.quote()
                self._send_json(status, payload)
                state.log(
                    {
                        "duration_ms": round(duration * 1000, 2),
                        "event": "synthetic_request",
                        "mode": mode,
                        "request_id": f"lab-{sequence}",
                        "route": "/quotes",
                        "status": status,
                    }
                )
                return
            self._send_json(404, {"error": "not found", "synthetic": True})

        def do_POST(self) -> None:
            if urlsplit(self.path).path != "/control":
                self._send_json(404, {"error": "not found", "synthetic": True})
                return
            if self.headers.get("X-Lab-Control") != CONTROL_MARKER:
                self._send_json(403, {"error": "control marker required", "synthetic": True})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = -1
            if length < 2 or length > 256:
                self._send_json(400, {"error": "invalid body size", "synthetic": True})
                return
            try:
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict) or set(payload) != {"action"}:
                    raise ValueError("invalid shape")
                result = state.change(payload["action"])
            except (json.JSONDecodeError, TypeError, ValueError):
                self._send_json(400, {"error": "invalid control action", "synthetic": True})
                return
            state.log({"event": "synthetic_control", **result})
            self._send_json(200, {"synthetic": True, **result})

    return Handler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bounded synthetic observability target")
    parser.add_argument("--host", default="127.0.0.1", choices=("127.0.0.1", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--seconds", type=int, default=600)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not 1 <= args.port <= 65535:
        raise SystemExit("port must be 1..65535")
    if not 1 <= args.seconds <= 2400:
        raise SystemExit("seconds must be 1..2400")
    state = LabState()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(state))
    server.timeout = 0.25
    stop = threading.Event()

    def request_stop(*_: object) -> None:
        stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    state.log({"event": "synthetic_ready", "port": server.server_port, "seconds": args.seconds})
    deadline = time.monotonic() + args.seconds
    try:
        while not stop.is_set() and time.monotonic() < deadline:
            server.handle_request()
    finally:
        server.server_close()
        state.log({"event": "synthetic_stopped"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
