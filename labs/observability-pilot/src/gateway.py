"""Fixed-destination TCP gateway from host loopback to the internal lab network."""

from __future__ import annotations

import json
import selectors
import signal
import socket
import socketserver
import threading
import time


ROUTES = {
    13000: ("grafana", 3000),
    18080: ("app", 8080),
    19090: ("prometheus", 9090),
}
CONNECTION_LIMIT = 32
CONNECTION_SECONDS = 60
BUFFER_BYTES = 65536
slots = threading.BoundedSemaphore(CONNECTION_LIMIT)


def _set_events(selector: selectors.BaseSelector, connection: socket.socket, events: int) -> None:
    try:
        selector.get_key(connection)
    except KeyError:
        if events:
            selector.register(connection, events)
    else:
        if events:
            selector.modify(connection, events)
        else:
            selector.unregister(connection)


def _relay(
    client: socket.socket,
    upstream: socket.socket,
    deadline: float,
    *,
    buffer_bytes: int = BUFFER_BYTES,
) -> tuple[int, int]:
    peers = {client: upstream, upstream: client}
    pending = {client: bytearray(), upstream: bytearray()}
    read_open = {client: True, upstream: True}
    write_shutdown = {client: False, upstream: False}
    uploaded = 0
    downloaded = 0

    def shutdown_write(connection: socket.socket) -> None:
        if write_shutdown[connection]:
            return
        try:
            connection.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        write_shutdown[connection] = True

    def refresh(connection: socket.socket, selector: selectors.BaseSelector) -> None:
        events = 0
        if read_open[connection] and len(pending[peers[connection]]) < buffer_bytes:
            events |= selectors.EVENT_READ
        if pending[connection]:
            events |= selectors.EVENT_WRITE
        _set_events(selector, connection, events)

    with selectors.DefaultSelector() as selector:
        refresh(client, selector)
        refresh(upstream, selector)
        while time.monotonic() < deadline:
            if not any(read_open.values()) and not any(pending.values()):
                break
            timeout = min(1.0, max(0.0, deadline - time.monotonic()))
            for key, mask in selector.select(timeout=timeout):
                connection = key.fileobj
                peer = peers[connection]
                if mask & selectors.EVENT_READ:
                    capacity = buffer_bytes - len(pending[peer])
                    if capacity:
                        try:
                            data = connection.recv(capacity)
                        except BlockingIOError:
                            pass
                        else:
                            if data:
                                pending[peer].extend(data)
                            else:
                                read_open[connection] = False
                                if not pending[peer]:
                                    shutdown_write(peer)
                            refresh(connection, selector)
                            refresh(peer, selector)
                if mask & selectors.EVENT_WRITE and pending[connection]:
                    try:
                        sent = connection.send(pending[connection])
                    except BlockingIOError:
                        continue
                    if sent == 0:
                        raise ConnectionResetError("gateway destination closed during write")
                    del pending[connection][:sent]
                    if connection is upstream:
                        uploaded += sent
                    else:
                        downloaded += sent
                    if not pending[connection] and not read_open[peer]:
                        shutdown_write(connection)
                    refresh(connection, selector)
                    refresh(peer, selector)
    return uploaded, downloaded


class FixedGateway(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        if not slots.acquire(blocking=False):
            return
        target = ROUTES[self.server.server_address[1]]
        started = time.monotonic()
        uploaded = 0
        downloaded = 0
        try:
            with socket.create_connection(target, timeout=2) as upstream:
                self.request.setblocking(False)
                upstream.setblocking(False)
                deadline = time.monotonic() + CONNECTION_SECONDS
                uploaded, downloaded = _relay(self.request, upstream, deadline)
        except (ConnectionError, OSError, TimeoutError) as error:
            print(json.dumps({"event": "gateway_error", "route": target[0], "type": type(error).__name__}), flush=True)
        finally:
            slots.release()
            print(
                json.dumps(
                    {
                        "downloaded_bytes": downloaded,
                        "duration_ms": round((time.monotonic() - started) * 1000, 2),
                        "event": "gateway_connection",
                        "route": target[0],
                        "uploaded_bytes": uploaded,
                    },
                    separators=(",", ":"),
                    sort_keys=True,
                ),
                flush=True,
            )


class GatewayServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    stopped = threading.Event()
    servers: list[GatewayServer] = []
    threads: list[threading.Thread] = []

    def request_stop(*_: object) -> None:
        stopped.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    for port in ROUTES:
        server = GatewayServer(("0.0.0.0", port), FixedGateway)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        server.timeout = 0.5
        server.request_queue_size = CONNECTION_LIMIT
        thread.start()
        servers.append(server)
        threads.append(thread)
    print(json.dumps({"event": "gateway_ready", "ports": sorted(ROUTES)}), flush=True)
    try:
        while not stopped.wait(0.5):
            pass
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
