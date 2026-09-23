"""Finite teaching sessions over the existing fixture-only controller."""
from __future__ import annotations

import argparse
import json
import re
import signal
import sys

from development_triage import DevelopmentTriage, PolicyViolation


ACTIONS = ("review", "approve", "reject", "reset", "check-paths")


class UsageError(ValueError):
    """Fixed public guidance for invalid command combinations."""


def run_session(action: str = "review", reviewed_hash: str | None = None) -> dict:
    if action not in ACTIONS:
        raise UsageError("Escolha review, approve, reject, reset ou check-paths.")
    if action == "approve":
        if not isinstance(reviewed_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", reviewed_hash):
            raise UsageError("Para aprovar, informe --reviewed-hash com os 64 caracteres do SHA-256 que você revisou.")
    elif reviewed_hash is not None:
        raise UsageError("--reviewed-hash só pode ser usado com approve.")

    with DevelopmentTriage() as controller:
        workspace = controller.workspace
        before = controller.fixture_snapshot()
        proposal = controller.prepare()
        report = {
            "schema_version": "1.0", "action": action, "scenario_id": proposal.scenario_id,
            "ticket": json.loads(controller.read_fixture("ticket.json")),
            "source": controller.read_fixture("repository/src/totals.py"),
            "test": controller.read_fixture("repository/tests/test_totals.py"),
            "hypothesis": proposal.hypothesis, "evidence": proposal.evidence,
            "proposed_tests": proposal.proposed_tests,
            "diff": proposal.diff_path.read_text(encoding="utf-8"), "diff_sha256": proposal.diff_sha256,
            "decision": controller.accept(proposal, None), "denied_paths": [],
            "reset_count": 0, "same_diff_after_reset": None,
        }
        if action in ("approve", "reject"):
            approval = {
                "issuer": "human-reviewer", "status": "approved" if action == "approve" else "denied",
                "scenario_id": proposal.scenario_id, "action": "accept-diff", "target": "ephemeral-diff",
                "artifact_version": proposal.artifact_version,
                "diff_sha256": reviewed_hash if action == "approve" else proposal.diff_sha256,
            }
            decision = controller.accept(proposal, approval)
            report["decision"] = {key: decision[key] for key in ("decision", "reason", "accepted")}
        if action == "check-paths":
            for path in ("../policy.json", "/etc/passwd", "repository/src/not-allowlisted.py"):
                try:
                    controller.read_fixture(path)
                except PolicyViolation:
                    report["denied_paths"].append(path)
                else:
                    raise AssertionError("allowlist invariant")
        report["ephemeral_artifacts"] = sorted(
            path.relative_to(workspace).as_posix() for path in workspace.rglob("*") if path.is_file()
        )
        controller.reset()
        report["reset_count"] += 1
        if action == "reset":
            controller.reset()
            report["reset_count"] += 1
            if any(workspace.iterdir()):
                raise AssertionError("reset invariant")
            report["same_diff_after_reset"] = controller.prepare().diff_sha256 == proposal.diff_sha256
            if not report["same_diff_after_reset"]:
                raise AssertionError("determinism invariant")
            controller.reset()
        report["fixture_unchanged"] = controller.fixture_snapshot() == before
        if not report["fixture_unchanged"] or any(workspace.iterdir()):
            raise AssertionError("cleanup invariant")
    report["workspace_removed"] = not workspace.exists()
    if not report["workspace_removed"]:
        raise AssertionError("temporary directory invariant")
    return report


def render(report: dict) -> str:
    lines = [
        "AGENTS-05 — Triagem de bugs", "Simulação local: nenhum código de exemplo é executado ou aplicado.",
        "", "1. Ticket e evidências", json.dumps(report["ticket"], ensure_ascii=False, indent=2),
        "Código sintético:", report["source"], "Teste sintético (somente leitura):", report["test"],
        "2. Hipótese", report["hypothesis"], "Evidências: " + ", ".join(report["evidence"]),
        "Testes propostos:", *["- " + test for test in report["proposed_tests"]],
        "", "3. Diff para revisão", report["diff"], "SHA-256: " + report["diff_sha256"],
        "", "4. Decisão", report["decision"]["decision"] + " / " + report["decision"]["reason"],
    ]
    if report["decision"]["accepted"]:
        lines.append("Aceite sintético registrado apenas na área temporária. Nenhuma correção foi aplicada.")
    elif report["action"] == "review":
        lines.append("Revise as evidências e o diff. Só depois escolha approve com --reviewed-hash ou reject.")
    elif report["decision"]["reason"] == "approval_not_bound_to_diff":
        lines.append("Hash diferente da proposta atual. Execute review novamente; não reutilize uma aprovação antiga.")
    for path in report["denied_paths"]:
        lines.append("Leitura recusada pela allowlist: " + path)
    if report["action"] == "reset":
        lines.append("Dois resets consecutivos concluídos; a nova proposta reproduziu o mesmo hash.")
    lines.extend(["", "5. Limpeza", "Fixtures preservadas. Arquivos e diretório temporários removidos.",
                  "Nenhum progresso foi salvo no curso. Uma nova execução recomeça a prática."])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prática sintética finita de agents-05; sem escrita no curso.")
    parser.add_argument("action", choices=ACTIONS, nargs="?", default="review")
    parser.add_argument("--reviewed-hash", help="SHA-256 da proposta que você revisou; obrigatório em approve")
    parser.add_argument("--json", action="store_true", help="Relatório estruturado para verificações")
    args = parser.parse_args(argv)
    try:
        report = run_session(args.action, args.reviewed_hash)
    except UsageError as error:
        print(str(error), file=sys.stderr)
        return 2
    except (OSError, AssertionError, KeyError, ValueError):
        print("Falha na prática. Confira a imagem, as fixtures e os limites; não desative o isolamento.", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True) if args.json else render(report))
    return 0


if __name__ == "__main__":
    if sys.platform == "linux":
        signal.alarm(20)
    raise SystemExit(main())
