from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import urllib.parse


ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "Dockerfile",
    "compose.yaml",
    "README.md",
    "DEPENDENCIES.md",
    "METRICS.md",
    "src/app.py",
    "src/loadgen.py",
    "src/control.py",
    "src/gateway.py",
    "prometheus/prometheus.yml",
    "grafana/provisioning/datasources/prometheus.yml",
    "grafana/provisioning/dashboards/dashboards.yml",
    "grafana/dashboards/aiops-observability.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


for relative in EXPECTED:
    require((ROOT / relative).is_file(), f"missing required file: {relative}")

for path in (ROOT / "src").glob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

dashboard = json.loads((ROOT / "grafana/dashboards/aiops-observability.json").read_text(encoding="utf-8"))
require(dashboard["uid"] == "aiops-observability-pilot", "dashboard uid changed")
require(len(dashboard["panels"]) >= 8, "dashboard state coverage is incomplete")
expressions = "\n".join(
    target["expr"] for panel in dashboard["panels"] for target in panel.get("targets", [])
)
for metric in (
    "lab_mode",
    "lab_http_requests_total",
    "lab_http_request_duration_seconds_bucket",
    "lab_resets_total",
    'up{job="synthetic-app"}',
):
    require(metric in expressions, f"dashboard missing query: {metric}")

compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
all_runtime = compose + "\n" + dockerfile
for image in (
    "python:3.13.15-alpine3.24",
    "prom/prometheus:v3.5.5",
    "grafana/grafana-oss:13.0.2",
):
    require(image in all_runtime, f"missing pinned image: {image}")
require(not re.search(r"(?im)^\s*(?:FROM|image:)\s+\S*:latest(?:\s|$)", all_runtime), "latest tag is forbidden")
require("internal: true" in compose, "runtime network must be internal")
for published in (
    '"127.0.0.1:18080:18080"',
    '"127.0.0.1:19090:19090"',
    '"127.0.0.1:13000:13000"',
):
    require(published in compose, f"missing loopback-only port: {published}")
for forbidden in ("docker.sock", "privileged: true", "network_mode: host", "pid: host", "ipc: host"):
    require(forbidden not in compose.lower(), f"forbidden Compose capability: {forbidden}")
require(compose.count('cap_drop: ["ALL"]') == 6, "every service must drop capabilities")
require(compose.count('security_opt: ["no-new-privileges:true"]') == 6, "every service must deny privilege escalation")
require(compose.count("read_only: true") == 6, "every service must have a read-only root filesystem")
for limit in ("cpus:", "mem_limit:", "pids_limit:", "max-size:", "stop_grace_period:"):
    require(compose.count(limit) >= 6, f"every service must define {limit}")
require('com.docker.network.bridge.enable_ip_masquerade: "false"' in compose, "host-access network must disable masquerade")
require('com.docker.network.bridge.host_binding_ipv4: "127.0.0.1"' in compose, "host-access network must default to loopback")
require(compose.count("ports:") == 1, "only the fixed gateway may publish ports")
require("--storage.tsdb.retention.time=1h" in compose, "Prometheus time retention missing")
require("--storage.tsdb.retention.size=128MB" in compose, "Prometheus size retention missing")
require("GF_ANALYTICS_REPORTING_ENABLED: \"false\"" in compose, "Grafana reporting must be disabled")
require("GF_ANALYTICS_CHECK_FOR_UPDATES: \"false\"" in compose, "Grafana update calls must be disabled")

source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "src").glob("*.py"))
for forbidden_target in ("169.254.169.254", "host.docker.internal", "0.0.0.0/0"):
    require(forbidden_target not in source, f"forbidden runtime target: {forbidden_target}")
urls = set(re.findall(r'https?://[^\"\'\s]+', source))
require(urls <= {"http://app:8080", "http://app:8080/quotes", "http://prometheus:9090"}, f"unexpected runtime URL: {sorted(urls)}")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
for phrase in (
    "docker compose --profile tools run --rm control degrade",
    "docker compose --profile tools run --rm control recover",
    "docker compose --profile tools run --rm control reset",
    "docker compose --profile tools run --rm control evidence",
    "docker compose down --volumes --remove-orphans",
    "Configuração válida ou testes unitários não substituem esse cenário executado em containers.",
    "Correção de arquitetura aprovada em 2026-09-08.",
):
    require(phrase in readme, f"runbook requirement missing: {phrase}")
require((ROOT / "DEPENDENCIES.md").is_file(), "dependency inventory missing")
for document in (ROOT / "README.md", ROOT / "DEPENDENCIES.md", ROOT / "METRICS.md"):
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
        if target.startswith(("https://", "http://", "#")):
            continue
        require(not target.startswith("file:"), f"unsafe documentation link in {document.name}")
        relative_target = urllib.parse.unquote(target.split("#", 1)[0])
        require((document.parent / relative_target).resolve().is_file(), f"broken link in {document.name}: {target}")

secret_pattern = re.compile(r"(?im)^\s*(?:password|passwd|api[_-]?key|access[_-]?token|secret[_-]?key)\s*[:=]")
text_suffixes = {"", ".md", ".py", ".yaml", ".yml", ".json"}
for path in ROOT.rglob("*"):
    if path.is_file() and path.suffix.lower() in text_suffixes and "evidence" not in path.parts:
        text = path.read_text(encoding="utf-8")
        require(not secret_pattern.search(text), f"secret-like assignment in {path.relative_to(ROOT)}")

print(json.dumps({"files_checked": len(EXPECTED), "panels": len(dashboard["panels"]), "static_validation": "passed"}, sort_keys=True))
