"""Synthetic qualification inside the bounded, offline agents-05 container only."""
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def assert_read_only(path):
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write("inert qualification marker")
    except OSError as error:
        require(error.errno == errno.EROFS, "expected_read_only_filesystem")
    else:
        path.unlink()
        raise AssertionError("unexpected_writable_mount")


def main():
    signal.alarm(20)
    started = time.perf_counter()
    require(sys.platform == "linux" and os.getuid() == 65532 and os.getgid() == 65532, "identity")
    require(sys.version_info[:3] == (3, 14, 7), "python_version")
    for module in ("pip", "ensurepip", "setuptools", "msgpack"):
        require(importlib.util.find_spec(module) is None, "installer_or_vendor_present")
    installed = Path("/lib/apk/db/installed").read_text()
    require("P:libuuid\nV:2.42.3-r1\n" in installed, "libuuid_patch")
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines() if ":" in line)
    require(int(status["CapEff"].strip(), 16) == 0, "capabilities")
    require(status["NoNewPrivs"].strip() == "1", "no_new_privileges")
    interfaces = [line.split(":", 1)[0].strip() for line in Path("/proc/net/dev").read_text().splitlines() if ":" in line]
    require(interfaces == ["lo"], "network_interfaces")
    assert_read_only(Path("/qualification-write-probe"))
    assert_read_only(Path("/opt/lab/fixtures/.qualification-write-probe"))
    sys.path.insert(0, "/opt/lab/src")
    from development_triage import DevelopmentTriage

    with DevelopmentTriage() as controller:
        workspace = controller.workspace
        require(workspace.is_relative_to(Path("/work")), "temporary_boundary")
        before = controller.fixture_snapshot()
        proposal = controller.prepare()
        require(controller.accept(proposal, None)["decision"] == "hold", "missing_approval")
        approval = {
            "issuer": "human-reviewer", "status": "approved", "scenario_id": proposal.scenario_id,
            "action": "accept-diff", "target": "ephemeral-diff", "artifact_version": proposal.artifact_version,
            "diff_sha256": proposal.diff_sha256,
        }
        require(controller.accept(proposal, {**approval, "diff_sha256": "0" * 64})["decision"] == "block", "wrong_approval")
        require(controller.accept(proposal, approval)["accepted"], "synthetic_acceptance")
        peak_workspace_bytes = sum(p.stat().st_size for p in workspace.rglob("*") if p.is_file())
        expected_diff = proposal.diff_sha256
        for _ in range(2):
            controller.reset()
            require(not any(workspace.iterdir()), "reset")
        for _ in range(100):
            repeated = controller.prepare()
            require(repeated.diff_sha256 == expected_diff, "determinism")
            controller.reset()
        require(controller.fixture_snapshot() == before, "fixture_immutability")
    require(not workspace.exists(), "temporary_cleanup")
    usage = resource.getrusage(resource.RUSAGE_SELF)
    cgroup = Path("/sys/fs/cgroup")
    limits = {name: (cgroup / name).read_text().strip() for name in ("memory.max", "memory.swap.max", "pids.max", "cpu.max")}
    require(limits == {"memory.max": "67108864", "memory.swap.max": "0", "pids.max": "16", "cpu.max": "50000 100000"}, "cgroup_caps")
    work = os.statvfs("/work")
    require(work.f_blocks * work.f_frsize == 8388608, "tmpfs_cap")
    print(json.dumps({
        "status": "passed", "python": sys.version.split()[0], "uid": os.getuid(), "gid": os.getgid(),
        "limits": limits, "rss_peak_kib": usage.ru_maxrss, "cpu_seconds": usage.ru_utime + usage.ru_stime,
        "elapsed_seconds": time.perf_counter() - started, "pids_current": int((cgroup / "pids.current").read_text()),
        "workspace_peak_bytes": peak_workspace_bytes, "tmpfs_bytes": work.f_blocks * work.f_frsize,
        "repeat_cycles": 100, "consecutive_resets": 2, "fixture_unchanged": True, "workspace_removed": True,
        "python_license_sha256": hashlib.sha256(Path("/usr/local/lib/python3.14/LICENSE.txt").read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
