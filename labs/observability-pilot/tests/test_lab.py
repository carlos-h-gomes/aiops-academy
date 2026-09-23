from __future__ import annotations

from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import socket
import sys
import threading
import time
import unittest
import urllib.error
import urllib.request


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import app  # noqa: E402
import gateway  # noqa: E402


class GatewayRelayTests(unittest.TestCase):
    def test_large_response_survives_nonblocking_backpressure(self) -> None:
        payload = bytes(range(256)) * 8192
        client_peer, gateway_client = socket.socketpair()
        gateway_upstream, upstream_peer = socket.socketpair()
        received = bytearray()
        thread_errors: list[BaseException] = []

        def send_response() -> None:
            try:
                upstream_peer.sendall(payload)
                upstream_peer.shutdown(socket.SHUT_WR)
            except BaseException as error:
                thread_errors.append(error)

        def receive_slowly() -> None:
            try:
                time.sleep(0.05)
                while chunk := client_peer.recv(4096):
                    received.extend(chunk)
                    time.sleep(0.0005)
            except BaseException as error:
                thread_errors.append(error)

        try:
            gateway_client.setblocking(False)
            gateway_upstream.setblocking(False)
            gateway_client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
            client_peer.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4096)
            client_peer.shutdown(socket.SHUT_WR)
            sender = threading.Thread(target=send_response)
            receiver = threading.Thread(target=receive_slowly)
            sender.start()
            receiver.start()

            uploaded, downloaded = gateway._relay(
                gateway_client,
                gateway_upstream,
                time.monotonic() + 10,
                buffer_bytes=8192,
            )
            sender.join(timeout=2)
            receiver.join(timeout=2)

            self.assertFalse(sender.is_alive())
            self.assertFalse(receiver.is_alive())
            self.assertEqual(thread_errors, [])
            self.assertEqual(received, payload)
            self.assertEqual(uploaded, 0)
            self.assertEqual(downloaded, len(payload))
        finally:
            client_peer.close()
            gateway_client.close()
            gateway_upstream.close()
            upstream_peer.close()


class LabApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = app.LabState(emit_logs=False)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.make_handler(cls.state))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self) -> None:
        self.control("reset")

    def get(self, path: str) -> tuple[int, bytes]:
        try:
            with self.opener.open(self.base + path, timeout=2) as response:
                return response.status, response.read(65536)
        except urllib.error.HTTPError as error:
            body = error.read(65536)
            status = error.code
            error.close()
            return status, body

    def control(self, action: str, *, marker: str = app.CONTROL_MARKER) -> tuple[int, dict[str, object]]:
        request = urllib.request.Request(
            self.base + "/control",
            data=json.dumps({"action": action}).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json", "X-Lab-Control": marker},
        )
        try:
            with self.opener.open(request, timeout=2) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            payload = json.load(error)
            status = error.code
            error.close()
            return status, payload

    def test_healthy_degraded_recovery_and_metrics(self) -> None:
        healthy_statuses = [self.get("/quotes")[0] for _ in range(4)]
        self.assertEqual(healthy_statuses, [200, 200, 200, 200])

        status, changed = self.control("degrade")
        self.assertEqual(status, 200)
        self.assertEqual(changed["mode"], "degraded")
        degraded_statuses = [self.get("/quotes")[0] for _ in range(4)]
        self.assertEqual(degraded_statuses.count(503), 3)

        metrics_status, metrics_body = self.get("/metrics")
        metrics = metrics_body.decode("utf-8")
        self.assertEqual(metrics_status, 200)
        self.assertIn('lab_http_requests_total{route="/quotes",status="503",mode="degraded"} 3', metrics)
        self.assertIn('lab_mode{mode="degraded"} 1', metrics)
        self.assertIn('le="0.5"} 4', metrics)

        status, changed = self.control("recover")
        self.assertEqual(status, 200)
        self.assertEqual(changed["mode"], "healthy")
        self.assertEqual(self.get("/quotes")[0], 200)

    def test_reset_is_safe_to_repeat_and_clears_workload_counters(self) -> None:
        self.get("/quotes")
        self.control("degrade")
        first_status, first = self.control("reset")
        second_status, second = self.control("reset")
        self.assertEqual((first_status, second_status), (200, 200))
        self.assertEqual(first["mode"], "healthy")
        self.assertEqual(second["mode"], "healthy")
        status, body = self.get("/state")
        summary = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(summary["requests_total"], 0)
        self.assertEqual(summary["errors_total"], 0)
        self.assertGreaterEqual(summary["resets_total"], 2)

    def test_control_rejects_missing_marker_unknown_action_and_oversize(self) -> None:
        status, _ = self.control("degrade", marker="wrong")
        self.assertEqual(status, 403)
        status, _ = self.control("unknown")
        self.assertEqual(status, 400)

        request = urllib.request.Request(
            self.base + "/control",
            data=b"{" + b"x" * 300 + b"}",
            method="POST",
            headers={"X-Lab-Control": app.CONTROL_MARKER},
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.opener.open(request, timeout=2)
        self.assertEqual(caught.exception.code, 400)
        caught.exception.close()

    def test_liveness_is_independent_from_functional_mode(self) -> None:
        self.control("degrade")
        health_status, health = self.get("/health")
        state_status, state = self.get("/state")
        self.assertEqual(health_status, 200)
        self.assertEqual(json.loads(health)["status"], "process-running")
        self.assertEqual(state_status, 200)
        self.assertEqual(json.loads(state)["mode"], "degraded")


if __name__ == "__main__":
    unittest.main()
