from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys
import urllib.parse


LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT / "src"))

from development_triage import (  # noqa: E402
    DevelopmentTriage,
    EXPECTED_CAPABILITIES,
    EXPECTED_READS,
    EXPECTED_WRITES,
)


EXPECTED_FILES = {
    "README.md",
    "DEPENDENCIES.md",
    "compose.yaml",
    "src/development_triage.py",
    "fixtures/development/policy.json",
    "fixtures/development/ticket.json",
    "fixtures/development/proposal.json",
    "fixtures/development/repository/src/totals.py",
    "fixtures/development/repository/tests/test_totals.py",
    "tests/validate_static.py",
    "tests/test_development_triage.py",
    "tests/runtime_probe.py",
    "image/Dockerfile",
    "image/strip_installer.py",
    "image/.dockerignore",
    "GUIDE.md",
    "runtime.env",
    "src/learning_session.py",
    "tests/test_learning_session.py",
}
IMAGE = "sha256:a3ec1ef54271cf9640728b8ad52d6ca382649cc383ff473e2ccf7d5d3ff7e368"
REQUIRED_VARIABLES = {
    "AGENTS_PLATFORM",
    "AGENTS_UID",
    "AGENTS_GID",
    "AGENTS_PIDS_LIMIT",
    "AGENTS_CPU_LIMIT",
    "AGENTS_MEMORY_LIMIT",
    "AGENTS_STOP_GRACE_PERIOD",
    "AGENTS_TMPFS_LIMIT",
    "AGENTS_LOG_MAX_SIZE",
    "AGENTS_LOG_MAX_FILES",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict:
    for relative in EXPECTED_FILES:
        require((LAB_ROOT / relative).is_file(), f"missing lab file:{relative}")

    source_path = LAB_ROOT / "src" / "development_triage.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_path))
    imported = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__"
    )
    require(
        imported == {"dataclasses", "difflib", "hashlib", "json", "pathlib", "tempfile"},
        f"unexpected controller imports:{sorted(imported)}",
    )
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    require(names.isdisjoint({"eval", "exec", "compile", "system", "popen"}), "dynamic execution primitive found")
    for forbidden in ("subprocess", "socket", "urllib", "requests", "gitpython"):
        require(forbidden not in source.casefold(), f"forbidden controller capability:{forbidden}")

    policy = json.loads((LAB_ROOT / "fixtures/development/policy.json").read_text(encoding="utf-8"))
    require(set(policy["allowlisted_reads"]) == EXPECTED_READS, "read allowlist changed")
    require(set(policy["ephemeral_writes"]) == EXPECTED_WRITES, "write allowlist changed")
    require(policy["capabilities"] == EXPECTED_CAPABILITIES, "capabilities changed")

    compose = (LAB_ROOT / "compose.yaml").read_text(encoding="utf-8")
    require(IMAGE in compose, "verified image reference missing")
    require('"/opt/lab/src/learning_session.py", "review"' in compose, "guided review must be the default")
    require("pull_policy: never" in compose, "local qualified artifact required")
    require('memswap_limit: "${AGENTS_MEMORY_LIMIT:?' in compose, "swap must not exceed memory")
    require("network_mode: \"none\"" in compose, "runtime network must be absent")
    require("read_only: true" in compose, "root filesystem must be read-only")
    require('cap_drop: ["ALL"]' in compose, "capabilities must be dropped")
    require('security_opt: ["no-new-privileges:true"]' in compose, "privilege escalation must be disabled")
    require(compose.count("type: bind") == 2 and compose.count("read_only: true") == 3, "mounts must be narrow and read-only")
    require("/work:size=${AGENTS_TMPFS_LIMIT:?" in compose, "ephemeral write boundary missing")
    for forbidden in (
        "docker.sock",
        "privileged: true",
        "network_mode: host",
        "host.docker.internal",
        "ports:",
        "build:",
        "latest",
    ):
        require(forbidden not in compose.casefold(), f"forbidden Compose capability:{forbidden}")
    variables = set(re.findall(r"\$\{([A-Z0-9_]+):\?[^}]+\}", compose))
    require(variables == REQUIRED_VARIABLES, f"runtime blocker variables changed:{sorted(variables)}")
    require(not re.search(r"\$\{[A-Z0-9_]+:-", compose), "runtime variable default is forbidden")

    readme = (LAB_ROOT / "README.md").read_text(encoding="utf-8")
    dependencies = (LAB_ROOT / "DEPENDENCIES.md").read_text(encoding="utf-8")
    for phrase in (
        "Qualificação local em linux/amd64",
        "não existe ferramenta para Git, commit, push, shell, subprocesso, rede, segredo",
        "licenças transitivas",
        "recursos",
    ):
        require(phrase.casefold() in (readme + dependencies).casefold(), f"documentation boundary missing:{phrase}")
    for document in (LAB_ROOT / "README.md", LAB_ROOT / "DEPENDENCIES.md", LAB_ROOT / "GUIDE.md"):
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if target.startswith(("https://", "#")):
                continue
            relative = urllib.parse.unquote(target.split("#", 1)[0])
            require((document.parent / relative).resolve().is_file(), f"broken local link:{document.name}:{target}")

    with DevelopmentTriage() as controller:
        before = controller.fixture_snapshot()
        proposal = controller.prepare()
        require(proposal.diff_path.is_relative_to(controller.workspace), "diff escaped temporary area")
        require(controller.accept(proposal, None)["decision"] == "hold", "approval must be external")
        controller.reset()
        require(controller.fixture_snapshot() == before, "fixture changed")
        require(not any(controller.workspace.iterdir()), "reset left artifacts")

    return {
        "files_checked": len(EXPECTED_FILES),
        "allowlisted_reads": len(EXPECTED_READS),
        "ephemeral_writes": len(EXPECTED_WRITES),
        "required_runtime_parameters": len(REQUIRED_VARIABLES),
        "docker_commands": 0,
        "static_validation": "passed",
    }


if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False, sort_keys=True))
