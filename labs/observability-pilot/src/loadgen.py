"""Fixed-target, fixed-rate synthetic load for the observability pilot."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


TARGET = "http://app:8080/quotes"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bounded synthetic load generator")
    parser.add_argument("--seconds", type=int, default=300)
    parser.add_argument("--interval", type=float, default=0.5)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not 1 <= args.seconds <= 1800:
        raise SystemExit("seconds must be 1..1800")
    if not 0.2 <= args.interval <= 5:
        raise SystemExit("interval must be 0.2..5 seconds")

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline = time.monotonic() + args.seconds
    next_request = time.monotonic()
    total = 0
    errors = 0
    timeouts = 0
    while time.monotonic() < deadline:
        total += 1
        status = 0
        try:
            with opener.open(TARGET, timeout=1) as response:
                status = response.status
                response.read(1024)
        except urllib.error.HTTPError as error:
            status = error.code
            error.close()
        except (TimeoutError, urllib.error.URLError):
            timeouts += 1
        if status >= 500 or status == 0:
            errors += 1
        if total == 1 or total % 20 == 0:
            print(
                json.dumps(
                    {
                        "errors": errors,
                        "event": "synthetic_load_progress",
                        "requests": total,
                        "timeouts": timeouts,
                    },
                    separators=(",", ":"),
                    sort_keys=True,
                ),
                flush=True,
            )
        next_request += args.interval
        time.sleep(max(0, next_request - time.monotonic()))

    print(
        json.dumps(
            {
                "errors": errors,
                "event": "synthetic_load_complete",
                "requests": total,
                "timeouts": timeouts,
            },
            separators=(",", ":"),
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
